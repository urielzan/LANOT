# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 15:29:17 2018

@author: LANOT02_UNAM
"""
# Required libraries
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from matplotlib.patches import Rectangle
from mpl_toolkits.basemap import Basemap
# Linear interpolation for color maps
#from matplotlib.colors import LinearSegmentedColormap 
# In python 3 use the version of GDAL 2.3.1 or higher
# In python 2.7 the version of gdal 2.2.4 does not cause many problems
from osgeo import gdal, osr
import os
import subprocess
import numpy as np
import time as t
# Import the CPT convert function
#from cpt_convert import loadCPT 

def extractNetCDF(path,var):
    """
    ==========================================================================================
    Function that obtains data from the NetCDF, can be adjusted to apply operations
    direct, example: data = data - 273.15, if you want the temperature in Celsius,
    the operation depends on the variable
    ==========================================================================================
    """    
    print('Extracting data...')

    # Open the nc file with the NetCDF4 module
    nc = Dataset(path)
    
    # Extract the values ​​of the variable, unmasking the values, generate a numpy.array
    data = nc.variables[var][:]
    data = np.ma.getdata(data)    
    qualData = nc.variables['DQF'][:]  
    #qualData = nc.variables['DQF_Overall'][:] 
    #qualData = nc.variables['DQF_Retrieval'][:] 
    #qualData = nc.variables['DQF_SkinTemp'][:]   
    
    # In case of entering the DQF as variable
    if var != 'DQF':
	    # Search and designate the null value, this value may vary according to the file
	    data[data == 65535.] = np.nan
    
	    
	    # Get the factor and offset
	    #scale = nc.variables[var].scale_factor
	    #offset = nc.variables[var].add_offset
	    
	    # Applies scale and offset
	    #data = data * scale + offset

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
    
    # It obtains data of the variable, they are required to put the information on the map
    varName = nc.variables[var].long_name
    stdName = nc.variables[var].standard_name
    units = nc.variables[var].units

    # Close the dataset
    nc.close()
    
    return data,qualData,x1,x2,y1,y2,varName,stdName,units

def windowsCoordinates(x,y,offset):
    """
    ==========================================================================================
    Function that obtains the extreme coordinates of both the temporary TIFF for extraction
    of data such as that required for mapping
    ==========================================================================================
    """
    print ('Getting window coordinates ...')    

    # Obtain the extreme coordinates of the window according to the offset
    urlon= x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
        
    return lllon,lllat,urlon,urlat

def createTiff(data, xmin, ymin, xmax, ymax, nx, ny):
    """
    ==========================================================================================    
    Function that creates a temporary TIFF for the simplest manipulation of data, this
    TIFF contains all the data of the variable in its original projection
    ==========================================================================================
    """     
    print ('Creating tif ...')
    
    # Parameters for the creation of the TIFF by GDAL
    xres = (xmax - xmin) / float(ny)
    yres = (ymax - ymin) / float(nx)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    dst_ds = gdal.GetDriverByName('GTiff').Create('tmp.tif', ny, nx, 1, gdal.GDT_Float32)
    
    # Apply geotransformation and projection
    dst_ds.SetGeoTransform(geotransform)    # Specific coordinates
    srs = osr.SpatialReference()            # Set the assembly
    srs.ImportFromProj4("+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs") # Projection Goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # Export the coordinate system
    dst_ds.GetRasterBand(1).WriteArray(data)   # Write the band to the raster
    dst_ds.FlushCache()                     # Write to the disk
    
    dst_ds = None
   
def reprojectTiff(x,y,offset):
    """
    ==========================================================================================
    Function that reprojects the TIFF, first to a geographic system and then cuts it out with
    the extreme coordinates calculated with the function coordinatesVentana, this is done by
    means of system commands, if GDAL is installed on the system it can be used the module 
    subprocess, if it causes problems try with the module os to call it from python
    ==========================================================================================
    """      
    print ('Reprojecting tif ...') 
    
    # Reproject the tif with geo-stationary coordinate system  to geographical
    #os.system('gdalwarp -t_srs EPSG:4326 tmp.tif tmp_4326.tif')
    subprocess.call('gdalwarp -dstnodata -9999.0 -t_srs EPSG:4326 -of Gtiff tmp.tif tmp_4326.tif')
    
    # Obtain the extreme coordinates of the window
    winCoor = []    
    winCoor = windowsCoordinates(x,y,offset)

    # Trim the tiff in geographic with the coordinates of the window
    #os.system('gdalwarp -te '+str(winCoor[0])+' '+str(winCoor[1])+' '+str(winCoor[2])+' '+str(winCoor[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_win.tif') 
    subprocess.call('gdalwarp -dstnodata -9999.0 -te '+str(winCoor[0])+' '+str(winCoor[1])+' '+str(winCoor[2])+' '+str(winCoor[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_win.tif')

def finderTiff(tif,x,y):
    """
    ==========================================================================================
    Function that finds the row and column of the desired coordinate, counting the number of
    pixels per unit of the difference of the extreme coordinates to the sought
    ==========================================================================================
    """    
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
    
    band = ds.GetRasterBand(1) # Create the array
    
    data = band.ReadAsArray() # Read the array
    
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
    """
    ==========================================================================================    
    Function that extracts the values ​​of the trimmed TIFF and converts them to a numpy array   
    ==========================================================================================
    """
    print ('Extracting tif...')
    
    # Extract tiff values ​​to a numpy array
    ds = gdal.Open('tmp_4326_win.tif')
    data = ds.ReadAsArray()
       
    # Eliminate temporary tiff
    os.remove('tmp.tif')
    os.remove('tmp_4326.tif')
    
    return data

def scanTime(path):
    """
    ==========================================================================================	
	Function that obtains the date and times of scanning from the name of the file
    ==========================================================================================
    """
    # Busca el tiempo de inicio de escaneo
    start = (path[path.find("s")+1:path.find("_e")])    
     
    # Busca el tiempo de finalizado de escaneo
    end = (path[path.find("e")+1:path.find("_c")])    
    
    # Le da formato al tiempo de observación    
    year = start[0:4]
    day = start[4:7]
    date = start[0:14]
    startTime =  start [7:9] + ":" + start [9:11] + ":" + start [11:13] + "." + start [13:14] 
    endTime = end [7:9] + ":" + end [9:11] + ":" + end [11:13] + "." + end [13:14]
            
    return year,day,startTime,endTime,date

def regionCoordinates(x,y):
    """
    ==========================================================================================	
	Function that obtains the quadrant of the coordinates sought according to their value
    ==========================================================================================
    """
    # Obtain the region according to the coordinates  
    if x < 0 and y > 0 :
        xName = 'W'
        yName = 'N'
    elif x > 0 and y > 0 :
        xName = 'E'
        yName = 'N'
    elif x < 0 and y < 0 :
        xName = 'W'
        yName = 'S'
    else : 
        xName = 'E'
        yName = 'S'
    
    return xName,yName

def calculateTicks(dataMin,dataMax):
    """
    ==========================================================================================    
	Function that calculates the numerical intervals of the symbology based on the values
    of the window, these can be increased if required
    ==========================================================================================
    """
    # Get the intervals based on the minimum and maximum values ​​within the window     
    if dataMin >= 0 :
        inter = dataMax - dataMin 
        
    elif dataMin < 0 and dataMax > 0:
        inter = dataMax + abs(dataMin)
        
    elif dataMin < 0 and dataMax <= 0:
        inter = abs(dataMin) - abs(dataMax)
     
    # Define the number of values ​​displayed in the color bar    
    tick1 = dataMin + inter/8
    tick2 = dataMin + inter*2/8
    tick3 = dataMin + inter*3/8
    tick4 = dataMin + inter*4/8
    tick5 = dataMin + inter*5/8
    tick6 = dataMin + inter*6/8
    tick7 = dataMin + inter*7/8     
    
    return tick1,tick2,tick3,tick4,tick5,tick6,tick7

def plotData(x,y,offset,var,path,winCoor,dataWin,dataMin,dataMax,dataMean,searchVar,varName,stdName,units,qualVar,palette,logoPath,showsData):
    """
    ==========================================================================================
    Function that maps the data of the window, requiring the numpy array created from
    of the TIFF data clipped and reprojected, in addition to showing the information of the
    variable
    ==========================================================================================
    """
    print ('Mapping data...')

    # Size of the figure
    fig = plt.figure(figsize=(15,15))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax = plt.axis('off')
    
    # Create the base map with the extreme coordinates
    bmap = Basemap(llcrnrlon=winCoor[0], llcrnrlat=winCoor[1], urcrnrlon=winCoor[2], urcrnrlat=winCoor[3], resolution='i', epsg=4326) 
    bmap.drawcoastlines(linewidth=1.5)
    bmap.drawcountries(linewidth=1.5)                    
    bmap.drawstates(linewidth=0.5)
    bmap.drawparallels(np.arange(-90.0, 90.0, offset/2.0), linewidth=0.5, color='black')
    bmap.drawmeridians(np.arange(0.0, 360.0, offset/2.0), linewidth=0.5, color='black')
    
    # Plot the data with the assigned palette
    bmap.imshow(dataWin, origin='upper', cmap=palette )
    
    # Add a color bar
    tick1,tick2,tick3,tick4,tick5,tick6,tick7 = calculateTicks(dataMin,dataMax)   
    
    # Add the values ​​of the intervals to the color bar
    cb = bmap.colorbar(location='bottom', size = '2.0%', pad = '-2.0%', ticks=[tick1,tick2,tick3,tick4,tick5,tick6,tick7])
    cb.ax.set_xticklabels([str(round(tick1,2)),str(round(tick2,2)),str(round(tick3,2)),str(round(tick4,2)),str(round(tick5,2)),str(round(tick6,2)),str(round(tick7,2))])
    cb.outline.set_visible(True) # Puts a line on the edge
    cb.ax.tick_params(width = 0) # Remove the ticks
    cb.ax.xaxis.set_tick_params(pad=-20) # Put the values ​​of the intervals inside the bar
    cb.ax.tick_params(axis='x', colors='black', labelsize=15) # Defines the color and size of the letter of the ticks
    
    # Add a label to the point
    label = str(round(float(searchVar),3))+'\n('+str(x)+','+str(y)+')'
    
    # Add a bookmark of the searched point   
    varx, vary = bmap(x,y)
    bmap.plot(varx, vary, marker='+',color='r', markersize=55)
    plt.text(x+(offset/15.0), y+(offset/15.0), label, fontsize=20)

    # Get the regions of the coordinates     
    xName,yName = regionCoordinates(x,y)

    # Get the date and scan times 
    year,day,startTime,endTime,date = scanTime(path)   
    
    if showsData == True:
	    # Add a rectangle to place the data
	    currentAxis = plt.gca()
	    currentAxis.add_patch(Rectangle((x-offset,  y-offset/1.04),offset*0.75 ,offset*0.11 , alpha=1, zorder = 3 ,facecolor='silver', ec="black", lw=1.0))
	     
	    # Add the data of the variable to the rectangle
	    plt.text(x-offset/1.02, y-offset/1.19, 'File: '+path[path.find("OR"):path.find("_s")]+'...\nVariable: '+var+' '+varName+'\nStandard Name: '
	            +stdName+'\nUnits: '+units, fontsize=12)

	    # Add the window data
	    plt.text(x-offset/1.02, y-offset/1.05, 'Maximum: '+str(round(dataMax,2))+'\nMinimum:  '+str(round(dataMin,2))+'\nMean:        '+str(round(dataMean,2)),fontsize=15)
	    
	    # Add coordinate data
	    plt.text(x-offset/1.38, y-offset/1.07,'\nLatitud:    '+str(abs(round(y,2)))+' '+yName+'\nLongitud: '+str(abs(round(x,2)))+' '+xName, fontsize=15)
	    
	    # Add the value and quality of the data according to the subdataset DQF, which defines the quality with which the data were calculated, it is found
	    # in all Goes NetCDF L1b and L2, it is defined by the color of the letter
	    if qualVar == 0:
	        qualColor = 'g'
	        quality = 'Processed algorithm'

	    elif qualVar == 16 or searchVar == np.nan:
	        qualColor = 'b'
	        quality = 'Unprocessed algorithm'
	    
	    else:
	        qualColor = 'r'
	        quality = 'Algorithm with quality: '+str(int(qualVar))

	    plt.text(x-offset/2.22,  y-offset/1.09,str(round(float(searchVar),2)), fontsize=30, color=qualColor)
	    plt.text(x-offset/2.24,  y-offset/1.06,quality,fontsize=7, color=qualColor)
    
    # Add the date and scan times
    plt.text(x-offset/1.02,y+offset/1.25,'Date: '+year+'-'+day+'\nSCANNING\nStart: '+startTime+'\nEnd: '+endTime,fontsize=23)
            
    # Add a logo
    logo = plt.imread(logoPath)
    plt.figimage(logo,965, 19, zorder=3, alpha = 1, origin = 'upper')
    
    # Save and show the map
    plt.savefig(path[path.find("OR"):path.find("_s")]+'_'+var+'_'+date+'_'+str(abs(y))+yName+'_'+str(abs(x))+xName+'.png')    
    plt.show()
    
def plotPixelSearch(path,var,x,y,offset,palette,logoPath,showsData):
    """
    ==========================================================================================
    This is the main function, find the value of a variable within a NetCDF L1b or L2 of Goes 16,
    obtaining a display window in geographic coordinates using the basemap module, in addition 
    to showing the quality of the data based on its value given in the data of quality DQF.

    Use GDAL system tools, incorporating them into Python through the module os or subprocess for
    trimming and reprojection.
    
    Requirements:
    Gdal 2.3.1 or higher in its desktop version.
    
    Parameters:
    path: is the path of the nc file, example: 'OR_ABI-L2-CMIPF-M3C01_G16_s20182761800374_e20182761811141_c20182761811213.nc'
    var: is the variable of the nc to search, you can use gdalinfo to know the correct name, example: 'LST'
    x: length in decimal degrees, with EPSG reference system: 4326, example: -99.19
    and: latitude in decimal degrees, with EPSG reference system: 4326, example: 19.19
    offset: is the extension of the window in degrees from the desired coordinate, example: 1.0
    palette: the name of the color palette predefined by matplotlib or created by the loadCPT function of cpt_covert, example: 'jet'
    logoPath: a logo in PNG format preferably 100X60 px, example: 'Logo.png'
    showsData: if you want to show the data of the variable, example: TRUE
    ==========================================================================================
    """
    
    # Start of the plotting process
    start = t.time()
    
    # Version of GDAL used
    #print (subprocess.call('gdalinfo --version'))
    
    print ('1. Extracting variable NetCDF4')

    data,qualData,x1,x2,y1,y2,varName,stdName,units = extractNetCDF(path,var)   
    
    # Get the dimensions of the array
    nx = data.shape[0]
    ny = data.shape[1]
    
    # Assign extreme coordinates
    xmin, ymin, xmax, ymax = [x1,y1,x2,y2]   
    
    print ('\n2. Obtaining variable data')

    # Create the TIFF
    createTiff(data, xmin, ymin, xmax, ymax, nx, ny )
    
    # Reproject the TIFF and cut it out
    reprojectTiff(x,y,offset)
    
    # Extracts values ​​from the reprojected and trimmed TIFF
    dataWin = extractTiff()

    # En caso de que el recorte haya sobrepasado la región de escaneo del Goes, al sobrante se le asigna nan  
    dataWin[dataWin == -9999.] = np.nan    

    # Obtiene los valore maximos, minimos y la media de la ventana
    dataMin = np.nanmin(dataWin)
    dataMax = np.nanmax(dataWin)
    dataMean = np.nanmean(dataWin)
    
    # Extract the TIFF value of the desired coordinate
    searchVar = finderTiff('tmp_4326_win.tif',x,y)
    
    # Clear the temporary TIFF
    os.remove('tmp_4326_win.tif')
    
    print ('\n3. Get quality data')

    # Obtain the desired pixel quality    
    createTiff(qualData, xmin, ymin, xmax, ymax, nx, ny )
    reprojectTiff(x,y,offset)
    extractTiff()
    qualVar = finderTiff('tmp_4326_win.tif',x,y)
    os.remove('tmp_4326_win.tif')
    
    print ('\n4. Plotting data')

    # Get the extreme coordinates of the window
    winCoor = windowsCoordinates(x,y,offset)
    
    # Plot the data
    plotData(x,y,offset,var,path,winCoor,dataWin,dataMin,dataMax,dataMean,searchVar,varName,stdName,units,qualVar,palette,logoPath,showsData)
    
    # Show the process information          
    print ('Region mapped in:', round(t.time() - start,4), 'segundos')
    print ('Latitude :',y)
    print ('Longitude :',x)
    print (var+' :',searchVar)


# FUNCTION TEST

# Uses the cpt covert function   
#cpt = loadCPT('temperature.cpt')
#cpt_convert = LinearSegmentedColormap('cpt', cpt)

# Path of the nc Goes16 file    
path = 'OR_ABI-L2-LSTF-M3_G16_s20182440000375_e20182440011141_c20182440016273.nc'
var = 'LST'
x = -90
y = 19
offset = 2
palette = 'Spectral'
logoPath = 'LANOT.png'
showsData = True

# Execute the function
plotPixelSearch(path,var,x,y,offset,palette,logoPath,showsData)
    
   