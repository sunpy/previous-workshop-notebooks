"""
Download level 1 EIS HDF5 files for 2021-04-24 and then fit the
Fe XII 195.119 profile to produce level 3 FITS files
"""
import eispac
import eispac.net  # This registers the EIS NRL client
from sunpy.net import Fido, attrs as a

if __name__ == '__main__':
    # Download the level 1 data
    q = Fido.search(
        a.Time('2021-04-24 04:00:00','2021-04-24 05:00:00'),
        a.Instrument('EIS'),
        a.Physobs.intensity,
        a.Source('Hinode'),
        a.Provider('NRL'),
        a.Level('1'),
    )
    files = Fido.fetch(q)
    files = sorted(files)

    # Read in the fitting templates
    template_names = [
        'fe_12_195_119.1c.template.h5',
    ]
    templates = [eispac.read_template(eispac.data.get_fit_template_filepath(t)) for t in template_names]

    # Fit level 1 data using each template and save out the intensity
    for t in templates:
        cube = eispac.read_cube(files[0], window=t.central_wave)
        fit_res = eispac.fit_spectra(cube, t, ncpu='max')
        m = fit_res.get_map(measurement='intensity')
        m.save(f"data/eis_{'_'.join(m.measurement.lower().split())}.fits", overwrite=True)