#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 14:15:21 2019

@author: lanot
"""
from pyproj import Proj, transform
from time import strftime,gmtime
import requests
#from osgeo import gdal
#import cartopy.crs as crrs
import os

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

def borraJPG(RGB):
    os.system('rm /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_Sentinel2/'+RGB+'/*')

def borraTodo():
    borraJPG('TC')
    borraJPG('SWIR')
    

def extraeWMS(x,y,offset,LAYERS,salida,path,RGB):

    coorVentana = coorVentanaSentinelHub(x,y,offset)    
    
    BBOX = str(coorVentana[0])+','+str(coorVentana[3])+','+str(coorVentana[2])+','+str(coorVentana[1])
    TIME = strftime("%Y-%m-%d", gmtime())
    #LAYERS = '1-NATURAL-COLOR,DATE'
    MAXCC = '10'
    
    if LAYERS != '1-NATURAL-COLOR,DATE':
        url = 'https://services.sentinel-hub.com/ogc/wms/b7b5e3ef-5a40-4e2a-9fd3-75ca2b81cb32?SERVICE=WMS&REQUEST=GetMap&MAXCC='+MAXCC+'&LAYERS='+LAYERS+'&EVALSOURCE=S2&WIDTH=1000&HEIGHT=1000&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+2019-01-30.jpg&TIME=2018-07-01/'+TIME+'&BBOX='+BBOX+'&PREVIEW=3&EVALSCRIPT=cmV0dXJuIFtCMTIqMi41LEI4QSoyLjUsQjAzKjIuNV0%3D'	
    #https://services.sentinel-hub.com/ogc/wms/b7b5e3ef-5a40-4e2a-9fd3-75ca2b81cb32?SERVICE=WMS&REQUEST=GetMap&MAXCC=20&LAYERS=2_COLOR_INFRARED__VEGETATION_,DATE&EVALSOURCE=S2&WIDTH=1840&HEIGHT=815&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+2019-01-31.jpg&TIME=2018-07-01/2019-01-31&BBOX=-495236,4890976,-356121,4953272&PREVIEW=3&EVALSCRIPT=cmV0dXJuIFtCMTIqMi41LEI4QSoyLjUsQjAzKjIuNV0%3D
    
    elif LAYERS ==  '1-NATURAL-COLOR,DATE':
        url = 'https://services.sentinel-hub.com/ogc/wms/b7b5e3ef-5a40-4e2a-9fd3-75ca2b81cb32?SERVICE=WMS&REQUEST=GetMap&MAXCC='+MAXCC+'&LAYERS='+LAYERS+'&EVALSOURCE=S2&WIDTH=1000&HEIGHT=1000&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+2019-01-30.jpg&TIME=2018-07-01/'+TIME+'&BBOX='+BBOX	
        
    r = requests.get(url)    
    code = open(path+RGB+'/'+salida+str(x)+"_"+str(y)+".jpg", "wb")
    code.write(r.content)
    code = None

    return 

#path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_Sentinel2/'
#extraeWMS(-103,20,1,'1-NATURAL-COLOR,DATE','TC_',path,'TC')
#extraeWMS(-103,20,1,'2_COLOR_INFRARED__VEGETATION_,DATE','SWIR_',path,'SWIR')

#borraTodo()

