# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 23:28:40 2019

@author: on_de
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from osgeo import gdal
import cartopy.crs as crrs
import os
from pyproj import Proj,transform


def archivoSentinel2(path):
    archivo = os.listdir(path)[0]
    return archivo

def coordenadasVentana(x,y,offset):
    print ('Obteniendo coordenadas ventana...')    

    # Obtiene las coordenadas extremas de la ventana de acuerdo al offset
    urlon= x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
    
    coorVentana = [lllon,urlat,urlon,lllat]    
    return coorVentana

def coorVentanaSentinelHub(x,y,offset):
    km = 111.12
    offset = offset*km*1000
    
    p1 = Proj(init='epsg:4326')
    p2 = Proj(init='epsg:3857')
    
    coorCent = transform(p1,p2,x,y)
    
    coorVentanaProj = coordenadasVentana(coorCent[0],coorCent[1],offset)
    
    return coorVentanaProj

def reproyectaJPG(x,y,offset,archivo):
    
    coorVentana = coorVentanaSentinelHub(x,y,offset) 

    ds = gdal.Open(archivo)

    gdal.Translate('tmp.tif',ds,options = gdal.TranslateOptions(outputBounds=coorVentana,outputSRS='EPSG:3857'))
    ds = gdal.Open('tmp.tif')
    gdal.Warp('tmp_4326.tif',ds,options=gdal.WarpOptions(dstSRS='EPSG:4326'))
    ds = None

    
def borraTmp():
    os.remove('tmp.tif')
    os.remove('tmp_4326.tif')
    
def plotRGB(coorVentana,x,y,salida):
    print ('Ploteando datos RGB...')   
        
    plt.figure(figsize=(10,10))
    
    ax = plt.axes(projection=crrs.PlateCarree())
    ax.coastlines(resolution='50m',color='w')
    #ax.gridlines(linestyle='--')
    ax.set_extent([coorVentana[0],coorVentana[2],coorVentana[3],coorVentana[1]])
    
    rgb = plt.imread('tmp_4326.tif')
    
    salida = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/output/'+salida
    
    plt.imshow(rgb,extent=[coorVentana[0],coorVentana[2],coorVentana[3],coorVentana[1]])
    plt.plot(x,y,'r+',markersize = 20)
                    
    imagen = salida+str(x)+'_'+str(y)+'.png'
    
    plt.savefig(imagen,dpi=300,bbox_inches='tight', pad_inches=0)
    
    rgb = None    

    return imagen
    
def RGBSentilen2(x,y,offset,RGB,path,salida):
    
    coorVentana = coordenadasVentana(x,y,offset)
    path = path+RGB
    
    archivo = archivoSentinel2(path)
    
    archivo = path+'/'+archivo

    
    reproyectaJPG(x,y,offset,archivo)
    
    imagen = plotRGB(coorVentana,x,y,salida) 
    
    borraTmp()    
   
    os.remove(archivo)

    return imagen
    
#path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_Sentinel2/'
#RGB = 'TC'
#x = -103
#y = 20
#offset = 1
#RGBSentilen2(x,y,offset,RGB,path,'Sentinel2_TC_')
#RGBSentilen2(x,y,offset,'SWIR',path,'Sentinel2_SWIR_')
