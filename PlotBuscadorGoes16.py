# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 15:29:17 2018

@author: LANOT02
"""

# Librerias requeridas
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from osgeo import gdal, osr
import os
import subprocess
import numpy as np
from mpl_toolkits.basemap import Basemap
import time as t



def extraeNetCDF(path,var):
    
    print ('Extrayendo variable netCDF4...')
    # Abre el archivo nc con em modulo netCDF4
    nc = Dataset(path)
    
    # Extrae los valores de la variable, desenmascarando los valores, geenera un numpy.array
    data = nc.variables[var][:]
    data = np.ma.getdata(data)
    
    # Busca y designa el valor nulo
    data[data == 65535] = np.nan
    
    # Obtiene los factores
    scale = nc.variables[var].scale_factor
    offset = nc.variables[var].add_offset
    
    # Aplica la escala y el offset
    data = data * scale + offset
    # EN caso de temperatura en Celsius
    #data = data -273.15
    
    # Convierte los datos en tipo flotante
    #data = data.astype('float32')
    
    # Obtiene la constante del punto de prespectiva y las multiplica por las coordenadas extremas
    H = nc.variables['goes_imager_projection'].perspective_point_height
    x1 = nc.variables['x_image_bounds'][0] * H
    x2 = nc.variables['x_image_bounds'][1] * H
    y1 = nc.variables['y_image_bounds'][1] * H
    y2 = nc.variables['y_image_bounds'][0] * H
           
    # Cierra el dataset
    nc.close()
    
    return data,x1,x2,y1,y2

def coordenadasVentana (x,y,offset):
    
    print ('Obteniendo coordenadas ventana...')    

    # Obtiene las coordenadas extremas de la ventana de acuerdo al offset
    urlon= x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
        
    return lllon,lllat,urlon,urlat

def creaTiff(data, xmin, ymin, xmax, ymax, nx, ny):
    
    print ('Creando tif...')
    
    # Parametros para la creacion del tiff por medio de GDAL
    xres = (xmax - xmin) / float(ny)
    yres = (ymax - ymin) / float(nx)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    dst_ds = gdal.GetDriverByName('GTiff').Create('tmp.tif', ny, nx, 1, gdal.GDT_Float32)
    
    # Aplica la geotransformacion y la proyeccion
    dst_ds.SetGeoTransform(geotransform)    # coordenadas especificas
    srs = osr.SpatialReference()            # establece el ensamble
    srs.ImportFromProj4("+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs") # Proeyeccion goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data)   # escribe la banda al raster
    dst_ds.FlushCache()                     # escribe en el disco
    
    dst_ds = None
   
def reproyectaTiff(x,y,offset):
    
    print ('Reproyectando tif...')
        
    #print urlon,urlat,lllat,lllon
    
    # Reproyecta el tif con sistema de coordenadas geoestacionario a geografico
    #os.system('gdalwarp -t_srs EPSG:4326 tmp.tif tmp_4326.tif')
    subprocess.call('gdalwarp -t_srs EPSG:4326 -of Gtiff tmp.tif tmp_4326.tif')
    
    # Obtiene las coordenadas extremas de la ventana
    coorven = []    
    coorven = coordenadasVentana(x,y,offset)

    # Recorta el tiff en geograficas con las coordenadas de la ventana
    #os.system('gdalwarp -te '+str(coorven[0])+' '+str(coorven[1])+' '+str(coorven[2])+' '+str(coorven[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_rec.tif') 
    subprocess.call('gdalwarp -te '+str(coorven[0])+' '+str(coorven[1])+' '+str(coorven[2])+' '+str(coorven[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_rec.tif')

def buscadorTif(tif,x,y):
    
    # Cordenadas buscadas
    points = [(x,y)]
    
    # Abre el raster 
    ds = gdal.Open(tif)
    
    # Si no lo puede abrir termina el proceso
    if ds is None:
        print ('No se pudo abrir el raster temporal')
        return 'sin calcular'        
    else:
        print ('Buscando pixel...')
    
    # Datos de la geotrasnformacion
    transform = ds.GetGeoTransform() 
    xOrigin = transform[0] # X de origen
    #print transform[0]
    yOrigin = transform[3] # Y de origen
    #print transform[3]
    pixelWidth = transform[1] # Tamaño de pixel
    #print transform[1]
    pixelHeight = transform[5] # Tamaño de pixel
    #print transform[5]
    
    band = ds.GetRasterBand(1) # crea el array
    
    data = band.ReadAsArray()
    
    # recorre las coordenadas de la ventana
    for point in points:
        x = point[0]
        y = point[1]
        
        # Obtiene los indices
        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / pixelHeight)
        #print xOffset
        #print yOffset
        
        # Obtiene el valor individual deacuerdo a los indices
        value = data[yOffset][xOffset]
        
    return value        
 
def extraeTiff():
    print ('Extrayendo tif...')
    
    # Extrae valores del tiff a un numpy array
    ds = gdal.Open('tmp_4326_rec.tif')
    data = ds.ReadAsArray()
       
    # Elimina los tif temporales
    os.remove('tmp.tif')
    os.remove('tmp_4326.tif')
    
    return data

    
def plotBuscador(path,var,x,y,offset):
    '''
    =======================================================================================================================
    Esta función encuentra el valor de una variable dentro de un NetCDF L1b o L2 de Goes 16, 
    obteniendo una ventana de visualización en coordenadas geográficas usando el módulo basemap, 
    usa herramientas de GDAL del sistema, incorporándolas a Python por medio del módulo os o subprocess 
    para el recorte y reproyección
    
    Parámetros:
    path: es la ruta del archivo nc, ejemplo: 'OR_ABI-L2-CMIPF-M3C01_G16_s20182761800374_e20182761811141_c20182761811213.nc'
    var: es la variable del nc a buscar, se puede usar gdalinfo para conocer el nombre correcto, ejemplo: 'LST'
    x: longitud en grados decimales, con sistema de referencia EPSG:4326
    y: latitud en grados decimales, con sistema de referencia EPSG:4326
    offset: es la extensión de la ventana en grados desde la coordenada buscada, ejemplo: 1.0  
    =======================================================================================================================
 
    '''
    # Inicio del proceso de ploteo
    start = t.time()
    
    #Version de GDAL utilizada
    #print (subprocess.call('gdalinfo --version'))
    
    data,x1,x2,y1,y2 = extraeNetCDF(path,var)   
    
    # Obtiene las dimensiones del array
    nx = data.shape[0]
    ny = data.shape[1]
    
    #  Asigna las coordenadas extremas
    xmin, ymin, xmax, ymax = [x1,y1,x2,y2]
    #xmin, ymin, xmax, ymax = [x2,y2,x1,y1]
    
    # Crea el tiff
    creaTiff(data, xmin, ymin, xmax, ymax, nx, ny )
    
    # Reproyecta el tif y lo recorta
    reproyectaTiff(x,y,offset)
    
    # Extrae valores del tiff reproyectado y recortado
    dataVen = extraeTiff()
    
    # Extrae el valor del tiff de la coordenada buscada
    varBus = buscadorTif('tmp_4326_rec.tif',x,y)
    
    # Borra el tiff temporal
    os.remove('tmp_4326_rec.tif')
    
    print ('Ploteando datos...')
    
    # Obtiene las coordenadas extremas de la ventana
    coorven = coordenadasVentana(x,y,offset)
    
    # Tamaño de la figura
    #plt.figure(figsize=(50,50))
    
    # Crea el mapa base con las coordenadas extremas
    bmap = Basemap(llcrnrlon=coorven[0], llcrnrlat=coorven[1], urcrnrlon=coorven[2], urcrnrlat=coorven[3], resolution='l', epsg=4326) 
    bmap.drawcoastlines(linewidth=0.5,color='#FF0049')
    #bmap.drawcountryes(linewidth=0.25)                    
    bmap.drawstates(linewidth=0.25)
    
    # Plotea los datos
    bmap.imshow(dataVen, origin='upper', cmap='Greys')
    
    # Agrega label al punto
    label = str(round(float(varBus),3))
    
    #Agrega marcador del punto buscado   
    estx, esty = bmap(x,y)
    bmap.plot(estx, esty, marker='+',color='r', markersize=25)
    plt.text(x+0.1, y+0.1, label)
    
    # Guarda y muestra el mapa
    #plt.savefig('buscador_'+var+'.png',dpi=100)    
    plt.show()
        
    # Show data
    #plt.imshow(dataVen, cmap='jet')
    #plt.show()
            
    print ('Region Mapeada en:', round(t.time() - start,4), 'segundos')
    print ('Latitud :',y)
    print ('Longitud :',x)
    print (var+' :',varBus)
    print ('\n')
    
    return varBus

# TEST DE LA FUNCION 
# Path del archivo nc Goes 16
#path = 'OR_ABI-L2-CMIPF-M3C01_G16_s20182761800374_e20182761811141_c20182761811213.nc'
#var = 'CMI'
#x = -99
#y = 19
#offset = 20

#plotBuscador(path,var,x,y,offset)
    
   