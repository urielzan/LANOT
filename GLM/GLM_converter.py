#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 16:59:54 2019

@author: lanot
"""

from netCDF4 import Dataset
#from mpl_toolkits.basemap import Basemap 
#import matplotlib.pyplot as plt
from time import strftime,strptime 
#import cartopy.crs as crrs
#import sys
import os
from glob import glob
#from osgeo import gdal
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
import shutil

def fecha(archivo):
    fechaStr = archivo[archivo.find('_e')+2:archivo.find('_c')-2]
    fechaStr = strptime(fechaStr,"%Y%j%H%M%S")
    fechaG16 = strftime("%Y-%m-%dT%H:%M:%SZ",fechaStr)
    ano = strftime("%Y",fechaStr)
    dia = strftime("%j",fechaStr)
    hora = strftime("%H",fechaStr)
    minuto = strftime("%M",fechaStr)
    fechaArch = ano+dia+hora+minuto
    
    return fechaStr,fechaG16,ano,dia,hora,minuto,fechaArch

def varDatos(ds,variable):
    if variable == 'event':
        lat = ds.variables[variable+'_lat'][:]
        lon = ds.variables[variable+'_lon'][:]   
        event_time = ds.variables[variable+'_time_offset'][:]
        #area = ds.variables[variable+'_area'][:]
        energy = ds.variables[variable+'_energy'][:]
        #quality = ds.variables[variable+'_quality_flag'][:]
        id_var = ds.variables[variable+'_id'][:]    
        return lat,lon,event_time,energy,id_var
    else :
        lat = ds.variables[variable+'_lat'][:]
        lon = ds.variables[variable+'_lon'][:]    
        area = ds.variables[variable+'_area'][:]
        energy = ds.variables[variable+'_energy'][:]
        quality = ds.variables[variable+'_quality_flag'][:]
        id_var = ds.variables[variable+'_id'][:]    
        return lat,lon,area,energy,quality,id_var

def generaGeom(lon,lat):
    geom = []
    for x,y in zip(lon,lat):
        coor = Point(x,y)
        geom.append(coor)
    
    return geom

def generaGDF (id_var,energy,area,quality,time,lon,lat,geom):
    df = pd.DataFrame({'id':id_var,'energy/J':energy,'area/m2':area,'quality':quality,'time':time,'lon':lon,'lat':lat,'geometry':geom} )    
    df = df[['id','energy/J','area/m2','quality','time','lon','lat','geometry']]    
    gdf = gpd.GeoDataFrame(df,geometry='geometry')    
    gdf.crs = '+proj=longlat +ellps=GRS80 +no_defs'
    
    return gdf

def generaGDF_event (id_var,energy,event_time,time,lon,lat,geom):
    df = pd.DataFrame({'id':id_var,'energy/J':energy,'t_offset/s':event_time,'time':time,'lon':lon,'lat':lat,'geometry':geom} )    
    df = df[['id','energy/J','t_offset/s','time','lon','lat','geometry']]    
    gdf = gpd.GeoDataFrame(df,geometry='geometry')    
    gdf.crs = '+proj=longlat +ellps=GRS80 +no_defs'
    
    return gdf
    
def generaShape(gdf,variable,ano,dia,hora,nombre):
    os.system('cd /data1/output/glm/shapefile/fd/;mkdir -p '+dia+'/'+hora)
    os.system('mkdir /data1/output/glm/shapefile/fd/'+dia+'/'+hora+'/'+nombre)
    gdf.to_file(filename='/data1/output/glm/shapefile/fd/'+dia+'/'+hora+'/'+nombre+'/'+nombre+'.shp',driver='ESRI Shapefile')
    shutil.make_archive('/data1/output/glm/shapefile/fd/'+dia+'/'+hora+'/'+nombre, 'zip','/data1/output/glm/shapefile/fd/'+dia+'/'+hora+'/'+nombre)
    #os.system('zip '+'./shapefiles/'+variable+'/'+fechaArch+'.zip'+' ./shapefiles/'+variable+'/'+fechaArch)
    os.system('cd '+'/data1/output/glm/shapefile/fd/'+dia+'/'+hora+'/'+nombre+';rm *')
    os.system('rm -r '+'/data1/output/glm/shapefile/fd/'+dia+'/'+hora+'/'+nombre)

def generaCSV(gdf,variable,ano,dia,hora,nombre):
    os.system('cd /data1/output/glm/csv/fd/;mkdir -p '+dia+'/'+hora)
    gdf.to_csv('/data1/output/glm/csv/fd/'+dia+'/'+hora+'/'+nombre+'.csv')  
    #os.system('zip '+'./csv/'+variable+'/'+fechaArch+'.zip'+' ./csv/'+variable+'/'+fechaArch+'.csv')
    #os.system('rm '+'./csv/'+variable+'/'+fechaArch)

def gmlProsesa(variable,glm,ano,dia,hora,nombre):
    if variable == 'event':
        lat,lon,event_time,energy,id_var = varDatos(glm,variable)    
        time = np.full(lat.shape,nombre) 
        geom = generaGeom(lon,lat) 
        gdf = generaGDF_event(id_var,energy,event_time,time,lon,lat,geom)
        generaShape(gdf,variable,ano,dia,hora,nombre)
        generaCSV(gdf,variable,ano,dia,hora,nombre)   
    
    else:   
        lat,lon,area,energy,quality,id_var = varDatos(glm,variable)    
        time = np.full(lat.shape,fechaG16) 
        geom = generaGeom(lon,lat) 
        gdf = generaGDF(id_var,energy,area,quality,time,lon,lat,geom)
        generaShape(gdf,variable,ano,dia,hora,nombre)
        generaCSV(gdf,variable,ano,dia,hora,nombre)    
    
#path = '/home/lanot/Documents/GML_data/'
#pathSalida = '/home/lanot/Documents/salida_gml/'

#archivos = glob('./data/*.nc*')
#archivos.sort()

#for i in archivos:

archivo_r = glob('/data1/input/glm/*.nc')
archivo_r.sort()
archivo_r = archivo_r[-15:]

print (archivo_r)

for i in archivo_r:
    print('Procesando archivo: '+i)
    glm = Dataset(i,'r')
    
    fechaStr,fechaG16,ano,dia,hora,minuto,fechaArch = fecha(i)
    
    archivo = i[i.find('OR'):-3]
    
    nombre = archivo[:archivo.find('G16_')]+'FLASH_'+archivo[archivo.find('LCFA_')+5:]
    gmlProsesa('flash',glm,ano,dia,hora,nombre)

    nombre = archivo[:archivo.find('G16_')]+'EVENT_'+archivo[archivo.find('LCFA_')+5:]    
    gmlProsesa('event',glm,ano,dia,hora,nombre)

    nombre = archivo[:archivo.find('G16_')]+'GROUP_'+archivo[archivo.find('LCFA_')+5:]    

    gmlProsesa('group',glm,ano,dia,hora,nombre)

    
