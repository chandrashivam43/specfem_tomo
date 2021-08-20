#!/usr/bin/env python

from specfem_tomo_helper.projection import vp2rho, vp2vs, vs2vp,  define_utm_projection
from specfem_tomo_helper.fileimport import Nc_model
from specfem_tomo_helper.utils import maptool, trilinear_interpolator, write_tomo_file
import matplotlib.pyplot as plt
import numpy as np

# INPUTS ARE HERE.
path = '../data/S362WMANI_kmps.nc'
dx = 10000
dy = 10000
z_min = 25  # in km
z_max = 2890  # in km
dz = 10000  # in m


# NO INPUT NEEDED PAST THIS LINE
# load netCDF model
nc_model = Nc_model(path)
# extract coordinates
lon, lat, depth = nc_model.load_coordinates()
# load model parameters
# In this case the interpolated model is Vsv.
vs = nc_model.load_variable('vs', fill_nan=False)

# define pyproj custom projection
myProj = define_utm_projection(11, 'N')
# Second mode is here, with graphical area selection for interpolation.
# The graphical selection tool takes an initial projection as argument. It can be modified using the GUI if it was not correctly specified.

mode = 1
if mode == 1:
    # Direct input akin to specfem Mesh_Par_File
    latitude_min = 3537939.0
    latitude_max = 3937939.0
    longitude_min = 330704.1
    longitude_max = 830704.1
    # Initialize interpolator with model and UTM projection
    gui_parameters = maptool(nc_model, myProj)
    interpolator = trilinear_interpolator(nc_model, gui_parameters.projection)
    interpolator.interpolation_parameters(longitude_min, longitude_max, dx,
                                          latitude_min, latitude_max, dy,
                                          z_min, z_max, dz)

if mode == 2:
    # Second mode with graphical area selection for interpolation.
    # The GUI window might freeze during the interpolation, instead of closing. Don't panic!
    gui_parameters = maptool(nc_model, myProj)
    interpolator = trilinear_interpolator(nc_model, gui_parameters.projection)
    interpolator.interpolation_parameters(
        gui_parameters.extent[0], gui_parameters.extent[1], dx,
        gui_parameters.extent[2], gui_parameters.extent[3], dy,
        z_min, z_max, dz)

tomo = interpolator.interpolate([vs])

# As we want Vp, Vsv and Rho to write the specfem files, we perform the following.
coordinates = tomo[:, 0:3]
vs = tomo[:, 3]
vp = vs2vp(vs)  # Convert Vsv to vp with empirical law
rho = vp2rho(vp)  # Converte vp to rho with empirical law
param = np.vstack((vp, vs, rho)).T  # Stack the three params

# Recombine the coordinates and the params in to the tomo array, [lon, lat, depth, vp, Vsv, rho] required to write.
tomo = np.hstack((coordinates, param))
# Write the tomography_file.xyz in "./" directory. It uses the tomography array and the interpolator parameters to produce the HEADER.
write_tomo_file(tomo, interpolator, './')

# Display the interpolated model.
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(tomo[:, 0], tomo[:, 1], tomo[:, 2], c=tomo[:, 3])
plt.show()
