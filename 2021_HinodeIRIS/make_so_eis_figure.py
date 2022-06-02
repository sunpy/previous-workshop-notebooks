import glob

from astropy.coordinates import SkyCoord
import astropy.time
import astropy.units as u
import astropy.wcs
from astropy.visualization import ImageNormalize, quantity_support
import eispac  # This registers the EISMap class
import matplotlib.pyplot as plt
import numpy as np
import pfsspy
from reproject import reproject_interp
import sunpy.coordinates
import sunpy.image.coalignment
import sunpy.map


def check_in_frame(coord,frame,corners):
    c_f = coord.transform_to(frame)
    in_lon = np.logical_and(c_f.Tx > corners[0].Tx, c_f.Tx < corners[1].Tx)
    in_lat = np.logical_and(c_f.Ty > corners[0].Ty, c_f.Ty < corners[1].Ty)
    in_frame = np.logical_and(in_lon, in_lat)
    return in_frame.any()


def get_loop_length(line):
    c = line.coords.cartesian.xyz
    s = np.append(0., np.linalg.norm(np.diff(c.value, axis=1), axis=0).cumsum()) * c.unit
    return np.diff(s).sum()


# Load maps
# Use this block in the event that the download is hanging.
files = sorted(glob.glob('data/*.f*ts'))
m_euvi, m_aia, m_eis, m_hmi, m_eui = sunpy.map.Map(files)

# Fix EIS pointing
n_x = (m_aia.scale.axis1 * m_aia.dimensions.x) / m_eis.scale.axis1
n_y = (m_aia.scale.axis2 * m_aia.dimensions.y) / m_eis.scale.axis2
m_aia_r = m_aia.resample(u.Quantity([n_x, n_y]))
yshift, xshift = sunpy.image.coalignment.calculate_shift(m_aia_r.data, m_eis.data)
reference_coord = m_aia_r.pixel_to_world(xshift, yshift)
Txshift = reference_coord.Tx - m_eis.bottom_left_coord.Tx
Tyshift = reference_coord.Ty - m_eis.bottom_left_coord.Ty
m_eis_fixed = m_eis.shift(Txshift, Tyshift)

# Crop maps
cropped_maps = []
small_fov_width = 300 * u.arcsec
small_fov_height = 300 * u.arcsec
eis_ar_center = SkyCoord(Tx=-350, Ty=-250, unit='arcsec',
                         frame=m_eis_fixed.coordinate_frame)
for m in [m_eis_fixed, m_aia, m_eui, m_euvi]:
    center = eis_ar_center.transform_to(m.coordinate_frame)
    blc = SkyCoord(center.Tx-small_fov_width/2,
                   center.Ty-small_fov_height/2,
                   frame=center.frame)
    cropped_maps.append(m.submap(
        blc, width=small_fov_width, height=small_fov_height))

# Do field extrapolation
shape_out=[540, 1080]
frame_out = SkyCoord(0, 0, unit=u.deg,
                     rsun=m_hmi.coordinate_frame.rsun, 
                     frame="heliographic_stonyhurst",
                     obstime=m_hmi.date)
header = sunpy.map.make_fitswcs_header(
    shape_out,
    frame_out,
    scale=[180 / shape_out[0], 360 / shape_out[1]] * u.deg / u.pix,
    projection_code="CAR",
)
out_wcs = astropy.wcs.WCS(header)
array, _ = reproject_interp(m_hmi, out_wcs, shape_out=shape_out)
array = np.where(np.isnan(array), 0, array)
m_hmi_cea = pfsspy.utils.car_to_cea(sunpy.map.Map(array, header))
m_hmi_cea.meta['TELESCOP'] = m_hmi.meta['TELESCOP']
m_hmi_cea.meta['CONTENT'] = 'Carrington Synoptic Chart Of Br Field'
m_hmi_cea.meta['T_OBS'] = m_hmi_cea.meta.pop('DATE-OBS')  # This is because of a bug where the date accidentally returns None if it is in the date-obs key
m_hmi_cea = sunpy.map.Map(
    m_hmi_cea.data,
    m_hmi_cea.meta,
)
nrho = 70
rss = 2.5
pfss_input = pfsspy.Input(m_hmi_cea, nrho, rss)
output = pfsspy.pfss(pfss_input)

# Trace fieldlines
masked_pix_y, masked_pix_x = np.where(m_hmi_cea.data < -3e1)
seeds = m_hmi_cea.pixel_to_world(
    masked_pix_x*u.pix, masked_pix_y*u.pix,).make_3d()
seeds_hpc = seeds.transform_to(m_eis_fixed.coordinate_frame)
in_lon = np.logical_and(seeds_hpc.Tx > m_eis_fixed.bottom_left_coord.Tx,
                        seeds_hpc.Tx < m_eis_fixed.top_right_coord.Tx)
in_lat = np.logical_and(seeds_hpc.Ty > m_eis_fixed.bottom_left_coord.Ty,
                        seeds_hpc.Ty < m_eis_fixed.top_right_coord.Ty)
seeds_eis = seeds[np.where(np.logical_and(in_lon, in_lat))]
tracer = pfsspy.tracing.FortranTracer()
fieldlines = tracer.trace(SkyCoord(seeds_eis), output,)

# Plot
fig = plt.figure(figsize=(10,5.25))
for i,m in enumerate([cropped_maps[0], cropped_maps[-2]]):
    ax = fig.add_subplot(1,2,i+1,projection=m)
    m.plot(axes=ax,
           title=f'{m.observatory} {m.instrument} {m.measurement}')
    bounds = ax.axis()
    for f in fieldlines[::3]:
        if get_loop_length(f) < 50 * u.Mm:
            continue
        if not check_in_frame(f.coords,
                              cropped_maps[0].coordinate_frame,
                              (cropped_maps[0].bottom_left_coord,
                              cropped_maps[0].top_right_coord)):
            continue
        ax.plot_coord(f.coords, ls='-', lw=1, color='C3', alpha=.75)
    ax.axis(bounds)
    #if i < 2:
    #    ax.coords[0].set_axislabel(' ')
    if i%2 != 0:
        ax.coords[1].set_axislabel(' ')
plt.subplots_adjust(wspace=0.175)
fig.savefig('eis-195-eui-174-ar-fieldlines.pdf')
