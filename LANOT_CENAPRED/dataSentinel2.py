#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 11:12:47 2019

@author: urielm
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
    print(BBOX)
    TIME = strftime("%Y-%m-%d", gmtime())
    #LAYERS = '1-NATURAL-COLOR,DATE'
    MAXCC = '10'
#https://services.sentinel-hub.com/ogc/wms/eadcc3e9-e764-4af4-9d3a-e191528a5262?SERVICE=WMS&REQUEST=GetMap&MAXCC=20&LAYERS=1-NATURAL-COLOR,DATE&CLOUDCORRECTION=none&EVALSOURCE=S2&TEMPORAL=false&WIDTH=1840&HEIGHT=869&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+2019-11-20.jpg&TIME=2015-01-01/2019-11-20&BBOX=-11239607,2235630,-10961376,2368477
    if LAYERS != '1-NATURAL-COLOR,DATE':
        #url = 'https://services.sentinel-hub.com/ogc/wms/eadcc3e9-e764-4af4-9d3a-e191528a5262?SERVICE=WMS&REQUEST=GetMap&MAXCC='+MAXCC+'&LAYERS='+LAYERS+'&EVALSOURCE=S2&WIDTH=1000&HEIGHT=1000&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+2019-01-30.jpg&TIME=2018-07-01/'+TIME+'&BBOX='+BBOX+'&PREVIEW=3&EVALSCRIPT=cmV0dXJuIFtCMTIqMi41LEI4QSoyLjUsQjAzKjIuNV0%3D'	
        url = 'https://services.sentinel-hub.com/ogc/wms/eadcc3e9-e764-4af4-9d3a-e191528a5262?SERVICE=WMS&REQUEST=GetMap&MAXCC='+MAXCC+'&LAYERS='+LAYERS+'&CLOUDCORRECTION=none&EVALSOURCE=S2&TEMPORAL=false&WIDTH=1000&HEIGHT=1000&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+'+TIME+'.jpg&TIME=2015-01-01/'+TIME+'&BBOX='+BBOX
    
        #https://services.sentinel-hub.com/ogc/wms/b7b5e3ef-5a40-4e2a-9fd3-75ca2b81cb32?SERVICE=WMS&REQUEST=GetMap&MAXCC=20&LAYERS=2_COLOR_INFRARED__VEGETATION_,DATE&EVALSOURCE=S2&WIDTH=1840&HEIGHT=815&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+2019-01-31.jpg&TIME=2018-07-01/2019-01-31&BBOX=-495236,4890976,-356121,4953272&PREVIEW=3&EVALSCRIPT=cmV0dXJuIFtCMTIqMi41LEI4QSoyLjUsQjAzKjIuNV0%3D
    
    elif LAYERS ==  '1-NATURAL-COLOR,DATE':
        #url = 'https://services.sentinel-hub.com/ogc/wms/b7b5e3ef-5a40-4e2a-9fd3-75ca2b81cb32?SERVICE=WMS&REQUEST=GetMap&MAXCC='+MAXCC+'&LAYERS='+LAYERS+'&EVALSOURCE=S2&WIDTH=1000&HEIGHT=1000&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+2019-01-30.jpg&TIME=2018-07-01/'+TIME+'&BBOX='+BBOX	
        url = 'https://services.sentinel-hub.com/ogc/wms/eadcc3e9-e764-4af4-9d3a-e191528a5262?SERVICE=WMS&REQUEST=GetMap&MAXCC='+MAXCC+'&LAYERS='+LAYERS+'&CLOUDCORRECTION=none&EVALSOURCE=S2&TEMPORAL=false&WIDTH=1000&HEIGHT=1000&ATMFILTER=ATMCOR&FORMAT=image/jpeg&NICENAME=Sentinel-2+image+on+'+TIME+'.jpg&TIME=2015-01-01/'+TIME+'&BBOX='+BBOX
        
    r = requests.get(url)    
    code = open(salida+str(x)+"_"+str(y)+".jpg", "wb")
    code.write(r.content)
    code = None

    return 

lat = 19.02
lon = -98.63
offset = 0.05
path = ''

extraeWMS(lon,lat,offset,'1-NATURAL-COLOR,DATE','TC_',path,'TC')
extraeWMS(lon,lat,offset,'2_COLOR_INFRARED__VEGETATION_,DATE','FC_',path,'FC')
extraeWMS(lon,lat,offset,'91_SWIR,DATE','SWIR_',path,'SWIR')
extraeWMS(lon,lat,offset,'5_VEGETATION_INDEX,DATE','NDVI_',path,'NDVI')

#borraTodo()
