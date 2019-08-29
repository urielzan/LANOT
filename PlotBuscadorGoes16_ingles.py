# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 15:29:17 2018

@author: LANOT02
"""

# Required libraries
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from osgeo import gdal, osr
import os
import subprocess
import numpy as np
from mpl_toolkits.basemap import Basemap
import time as t


def extractNetCDF(path,var):
    
    print ('Extracting variable netCDF4 ...')
    # Open the nc file with the netCDF4 module
    nc = Dataset(path)
    
    # Extract the values ​​of the variable, unmasking the values, generate a numpy.array
    data = nc.variables[var][:]
    data = np.ma.getdata(data)
    
    # Find and designate the null value
    data[data == 65535] = np.nan
    
    # Get the factor and offset
    scale = nc.variables[var].scale_factor
    offset = nc.variables[var].add_offset
    
    # Applies scale and offset
    data = data * scale + offset

    # In case of variable temperature in Celsius
    #data = data -273.15
    
    # Convert the data to floating type
    #data = data.astype('float32')
    
    # Obtain the constant of the perspective point and multiply them by the extreme coordinates
    H = nc.variables['goes_imager_projection'].perspective_point_height
    x1 = nc.variables['x_image_bounds'][0] * H
    x2 = nc.variables['x_image_bounds'][1] * H
    y1 = nc.variables['y_image_bounds'][1] * H
    y2 = nc.variables['y_image_bounds'][0] * H
           
    # Close the dataset
    nc.close()
    
    return data,x1,x2,y1,y2

def windowsCoordinates(x,y,offset):
    
    print ('Getting window coordinates ...')    

    # Obtain the extreme coordinates of the window according to the offset
    urlon= x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
        
    return lllon,lllat,urlon,urlat

def createTiff(data, xmin, ymin, xmax, ymax, nx, ny):
    
    print ('Creating tif ...')
    
    # Parameters for the creation of the tiff by GDAL
    xres = (xmax - xmin) / float(ny)
    yres = (ymax - ymin) / float(nx)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    dst_ds = gdal.GetDriverByName('GTiff').Create('tmp.tif', ny, nx, 1, gdal.GDT_Float32)
    
    # Apply geotransformation and projection
    dst_ds.SetGeoTransform(geotransform)    # specific coordinates
    srs = osr.SpatialReference()            # set the assembly
    srs.ImportFromProj4("+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs") # Projection Goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # export the coordinate system
    dst_ds.GetRasterBand(1).WriteArray(data)   # write the band to the raster
    dst_ds.FlushCache()                     # write to the disk
    
    dst_ds = None
   
def reprojectTiff(x,y,offset):
    
    print ('Reprojecting tif ...')
        
    #print (urlon,urlat,lllat,lllon)
    
    # Reproject the tif with geo-stationary coordinate system  to geographical
    #os.system('gdalwarp -t_srs EPSG:4326 tmp.tif tmp_4326.tif')
    subprocess.call('gdalwarp -t_srs EPSG:4326 -of Gtiff tmp.tif tmp_4326.tif')
    
    # Obtain the extreme coordinates of the window
    winCoor = []    
    winCoor = windowsCoordinates(x,y,offset)

    # Trim the tiff in geographic with the coordinates of the window
    #os.system('gdalwarp -te '+str(coorven[0])+' '+str(coorven[1])+' '+str(coorven[2])+' '+str(coorven[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_win.tif') 
    subprocess.call('gdalwarp -te '+str(wincoor[0])+' '+str(wincoor[1])+' '+str(wincoor[2])+' '+str(wincoor[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_win.tif')

def FinderTiff(tif,x,y):
    
    # Wanted coordinates
    points = [(x,y)]
    
    # Open the raster
    ds = gdal.Open(tif)
    
    # If you can not open it, the process ends
    if ds is None:
        print ('The temporary raster could not be opened')
        return 'without calculating'        
    else:
        print ('Looking for pixel ..')
    
    # Geotransformation data
    transform = ds.GetGeoTransform() 
    xOrigin = transform[0] # X of origin
    #print transform[0]
    yOrigin = transform[3] # Y of origin
    #print transform[3]
    pixelWidth = transform[1] # Pixel size
    #print transform[1]
    pixelHeight = transform[5] # Pixel size
    #print transform[5]
    
    band = ds.GetRasterBand(1) # crea el array
    
    data = band.ReadAsArray()
    
    # Go through the coordinates of the window
    for point in points:
        x = point[0]
        y = point[1]
        
        # Get indexes
        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / pixelHeight)
        #print xOffset
        #print yOffset
        
        # Obtain the individual value of the variable according to the indices
        value = data[yOffset][xOffset]
        
    return value        
 
def extractTiff():
    print ('Extracting tif...')
    
    # Extract tiff values ​​to a numpy array
    ds = gdal.Open('tmp_4326_win.tif')
    data = ds.ReadAsArray()
       
    # Eliminate temporary tiff
    os.remove('tmp.tif')
    os.remove('tmp_4326.tif')
    
    return data

    
def plotFinder(path,var,x,y,offset):
    """
    =========================================================================================================================
    This function finds the value of a variable within a NetCDF L1b or L2 of Goes 16,
    obtaining a display window in geographic coordinates using the basemap module,
    uses GDAL system tools, incorporating them into Python through the os module or subprocess
    for trimming and reprojection
    
    Parameters:
    path: is the path of the nc file, example: 'OR_ABI-L2-CMIPF-M3C01_G16_s20182761800374_e20182761811141_c20182761811213.nc'
    var: is the variable of the nc to search, you can use gdalinfo to know the correct name, example: 'LST'
    x: length in decimal degrees, with EPSG reference system: 4326
    and: latitude in decimal degrees, with EPSG reference system: 4326
    offset: is the extension of the window in degrees from the desired coordinate, example: 1.0
    =========================================================================================================================
    """
    
    # Start of the plotting process
    start = t.time()
    
    # Version of GDAL used
    #print (subprocess.call('gdalinfo --version'))
    
    data,x1,x2,y1,y2 = extractNetCDF(path,var)   
    
    # Get the dimensions of the array
    nx = data.shape[0]
    ny = data.shape[1]
    
    # Assign extreme coordinates
    xmin, ymin, xmax, ymax = [x1,y1,x2,y2]
    #xmin, ymin, xmax, ymax = [x2,y2,x1,y1]
    
    # Create the tiff
    createTiff(data, xmin, ymin, xmax, ymax, nx, ny )
    
    # Reproject the tiff and cut it out
    reprojectTiff(x,y,offset)
    
    # Extracts values ​​from the reprojected and trimmed tiff
    dataWin = extractTiff()
    
    # Extract the tiff value of the desired coordinate
    searchVar = FinderTiff('tmp_4326_win.tif',x,y)
    
    # Clear the temporary tiff
    os.remove('tmp_4326_win.tif')
    
    print ('Plotting data...')
    
    # Get the extreme coordinates of the window
    winCoor = windowsCoordinates(x,y,offset)
    
    # Size of the figure
    #plt.figure(figsize=(50,50))
    
    # Create the base map with the extreme coordinates
    bmap = Basemap(llcrnrlon=winCoor[0], llcrnrlat=winCoor[1], urcrnrlon=winCoor[2], urcrnrlat=winCoor[3], resolution='l', epsg=4326) 
    bmap.drawcoastlines(linewidth=0.5)
    bmap.drawcountryes(linewidth=0.25)                    
    bmap.drawstates(linewidth=0.25)
    
    # Plot the data
    bmap.imshow(dataWin, origin='upper', cmap='Greys')
    
    # Add label to the point
    label = str(round(float(searchVar),3))
    
    # Add bookmark of searched point   
    varx, vary = bmap(x,y)
    bmap.plot(varx, vary, marker='+',color='r', markersize=25)
    plt.text(x+0.1, y+0.1, label)
    
    # Save and show the map
    #plt.savefig('buscador_'+var+'.png',dpi=100)    
    plt.show()        
  
    print ('Region Mapped in:', round(t.time() - start,4), 'seconds')
    print ('Latitude :',y)
    print ('Longitude :',x)
    print (var+' :',searchVar)
    print ('\n')
    
    return searchVar

# FUNCTION TEST
# Path of the nc Goes16 file
#path = 'OR_ABI-L2-LSTF-M3_G16_s20182440000375_e20182440011141_c20182440016273.nc'
#var = 'LST'
#x = -99
#y = 19
#offset = 1

# Execute the function
#plotFinder(path,var,x,y,offset)
    
   