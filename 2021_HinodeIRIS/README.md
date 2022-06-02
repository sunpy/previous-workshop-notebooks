# SunPy Tutorial at the Hinode-14/IRIS-11 Meeting

This repo contains the notebook and needed data for the SunPy tutorial presented at the [*Hinode* 14/IRIS 11 Joint Science Meeting]() on 29 October 2021.

* To run this tutorial notebook in the cloud (recommended, no installation needed!), simply click this badge - [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/wtbarnes/hinode-iris-2021-sunpy-tutorial/HEAD).
* If you want to run this notebook locally, clone the repo and install the requirements in `requirements.txt`.

This tutorial will demonstrate how the `sunpy` core package, along with several affiliated packages as well as the `eispac` software, can be used to analyze an active region as observed by multiple observatories from drastically different viewpoints. This tutorial will emphasize the three core areas of functionality that `sunpy` provides:

* Data search and download
* Data containers for commonly used data products
* Coordinate transformations and reprojections between solar coordinate systems

Additionally, this tutorial will emphasize how other packages can both utilize and augment the capabilities provided by the `sunpy` core package. In particular, we emphasize the use of level 3 EIS observations in conjunction with other observatories, especially the Extreme Ultraviolet Imager (EUI) on *Solar Orbiter*.
