#!/usr/bin/env python

from specfem_tomo_helper.projection import vp2rho, vp2vs, vs2vp,  define_utm_projection
from specfem_tomo_helper.fileimport import Nc_model
from specfem_tomo_helper.utils import maptool, bilinear_interpolator, write_tomo_file
import subprocess
import os

path = '../data/S362WMANI_kmps.nc'

#if not os.path.isfile(path):
   # subprocess.call(['wget', '-P', '../data/', 'http://ds.iris.edu/files/products/emc/emc-files/3D2018-08Sv-depth.nc'])

# Mandatory inputs:
dy = 2000  # in m
dx = 2000  # in m
# In the 2D interpolation scheme, each depth value of the model is used as depth value. Therefore there is no dz parameters.
z_min = 24.4 # in km
z_max = 2891 # in km

# load netCDF model
nc_model = Nc_model(path)
# extract coordinates
lon, lat, depth = nc_model.load_coordinates()

# Load the 3 model parameters from the netCDF model
vs = nc_model.load_variable('vs', fill_nan=True)
vsv = nc_model.load_variable('vsv', fill_nan=True)
vsh = nc_model.load_variable('vsh', fill_nan=True)

# fill_nan is set to True here, as the shallow layers of the model contain nan values

# define pyproj custom projection. 11 North for South California
myProj = define_utm_projection(11, 'N')

# Here are two example modes possible (1 or 2)
# 1 for direct input, 2 for GUI map input
mode = 1
if mode == 1:
    # Direct input akin to specfem Mesh_Par_File
    latitude_min = 3537939.0
    latitude_max = 3937939.0
    longitude_min = 330704.1
    longitude_max = 830704.1
    # Initialize interpolator with model and UTM projection
    interpolator = bilinear_interpolator(nc_model, myProj)
    interpolator.interpolation_parameters(longitude_min, longitude_max, dx,
                                          latitude_min, latitude_max, dy,
                                          z_min, z_max)
#mode 2 is not working showing error of showing exceeding lat/lon limits (set coordinates accordingly)
if mode == 2:
    # Second mode with graphical area selection for interpolation.
    # The GUI window might freeze during the interpolation, instead of closing. Don't panic!
    gui_parameters = maptool(nc_model, myProj)
    interpolator = bilinear_interpolator(nc_model, myProj)
    interpolator.interpolation_parameters(
        gui_parameters.extent[0], gui_parameters.extent[1], dx,
        gui_parameters.extent[2], gui_parameters.extent[3], dy,
        z_min, z_max)

# Compute the tomography array
tomo = interpolator.interpolate([vs, vsv, vsh])
# Write the tomography_file.xyz in "./" directory. It uses the tomography array and the interpolator parameters to produce the HEADER.
write_tomo_file(tomo, interpolator, './')

