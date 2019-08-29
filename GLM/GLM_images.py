#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 10:25:19 2019

@author: lanot
"""

import matplotlib
matplotlib.use('Agg')
from netCDF4 import Dataset
#from mpl_toolkits.basemap import Basemap 
import matplotlib.pyplot as plt
from time import strftime,strptime 
import cartopy.crs as crrs
#from cartopy.feature import NaturalEarthFeature, LAND, COASTLINE
#from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
#import sys
#import os
from glob import glob
from pyproj import Proj,transform
from time import time
import geopandas as gpd
from PIL import Image
import numpy as np

def fecha(archivo):
    fechaStr = archivo[archivo.find('_e')+2:archivo.find('_c')-1]
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
    
#path = '/home/lanot/Documents/GML_data/'
#pathSalida = '/home/lanot/Documents/salida_gml/'

start = time()

#archivo_r = glob('/data1/input/glm/*.nc*')
archivo_r = glob('/data1/input/glm/*.nc')
archivo_r.sort()
archivo_r = archivo_r[len(archivo_r)-30:-15]
#185

#for i in archivos:

#archivo_r = glob('/data1/input/glm/*.nc')
#archivo_r.sort()

for i in archivo_r:
    
#archivo_r = archivo_r[-1]

    print('Procesando archivo: '+i)
    
    glm = Dataset(i,'r')
       
    fechaStr,fechaG16,ano,dia,hora,minuto,fechaArch = fecha(i)
        
    archivo = i[i.find('OR'):-3]
        
    nombre = archivo[:archivo.find('G16_')]+'IMAGE_'+archivo[archivo.find('LCFA_')+5:]
    
    plt.figure(figsize=(35, 25))
    
    ax = plt.axes(projection = crrs.Geostationary(central_longitude=-75.2,satellite_height=35786023.0,globe=crrs.Globe(ellipse='GRS80')))
    #ax.coastlines(resolution='10m',color='w',linewidth=0.5)
    
    #ax.add_feature(LAND)
    #ax.add_feature(COASTLINE)
    #states = NaturalEarthFeature(category='cultural', scale='50m', facecolor='none',
     #                        name='admin_1_states_provinces_shp')
    #_ = ax.add_feature(states, edgecolor='gray')
    
    coastlines = gpd.read_file('/home/lanotadm/data/shapefiles/ne_10m_coastline_g16/ne_10m_coastline_g16.shp')
    ax = coastlines.plot(axes=ax,color='',linewidth=0.75,edgecolor='#b6b6b6')
    
    shpMuni = gpd.read_file('/home/lanotadm/data/shapefiles/dest2018g16/dest2018g16.shp')
    ax = shpMuni.plot(axes=ax,color='',linewidth=0.75,edgecolor='#b6b6b6')
    
    #ax.set_global()
    #plt.plot(-3627271.341,1382771.948,'r.')
    #plt.plot(1583173.792,4589199.765,'b.')
    
    ax.set_extent([-113.08581162013971,-62.21829839632282,15.3,50.5], crs=crrs.PlateCarree())
    
    lat,lon,area,energy,quality,id_var = varDatos(glm,'group')
    p1 = Proj('+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.2 +sweep=x +no_defs')
    p2 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    x,y = transform(p2,p1,lon,lat)
    ax.plot(x,y,'o',markersize=2.5,color='#fffdc7',alpha = 0.01)
        
    lat,lon,event_time,energy,id_var = varDatos(glm,'event')
    p1 = Proj('+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.2 +sweep=x +no_defs')
    p2 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    x,y = transform(p2,p1,lon,lat)
    ax.plot(x,y,'o',markersize=2.5,color='#fffb8a',alpha = 0.02)
                           
    lat,lon,area,energy,quality,id_var = varDatos(glm,'flash')
    p1 = Proj('+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.2 +sweep=x +no_defs')
    p2 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    x,y = transform(p2,p1,lon,lat)
    ax.plot(x,y,'o',markersize=2.5,color='#fff700',alpha = 0.2)
    
    #plt.gca().legend(('group','event','flash'),loc='lower left',fontsize=18,facecolor='white')

# ====================================
# TEMPORAL!!!! SE CAMBIA A L1b-Rad
# ====================================

    cmi_data = None    
    
    print "Minuto: "+minuto
    print "Hora: "+hora
    print "Dia: "+dia

    if minuto == '59' and hora != '23':
        print('SIII 59')
        hora = "{:02d}".format(int(hora) + 1)
        minuto = '00'
        
    if minuto == '59' and hora == '23':
        print('SIII 59 23')
        hora = '00'
        minuto = '00'
        dia = str(int(dia) + 1)
    
    if (minuto == '00' or minuto == '01' or minuto == '02' or minuto == '03' or minuto == '04') and hora != '00':
        print('SIII 00')
        hora = "{:02d}".format(int(hora) - 1)
        minuto = "{:02d}".format(abs(int(minuto) - 59))
    
    if (minuto == '00' or minuto == '01' or minuto == '02' or minuto == '03' or minuto == '04') and hora == '00':
        print('SIII 00 00')
        hora = "{:02d}".format(abs(int(hora) - 23))
        minuto = "{:02d}".format(abs(int(minuto) - 59))
        dia = "{:02d}".format(int(dia) - 1)
        
    for j in range(6):          
        if len(glob('/data1/output/abi/l2/conus/*CMI*C13*_e'+ano+dia+"{:02d}".format(int(hora))+"{:02d}".format(int(minuto)-j)+'*_c*.nc*')) == 1:
            
            cmi_data = glob('/data1/output/abi/l2/conus/*CMI*C13*_e'+ano+dia+"{:02d}".format(int(hora))+"{:02d}".format(int(minuto)-j)+'*_c*.nc*')[0]
            
    print cmi_data
    
    fechaStr_cmi,fechaG16_cmi,ano_cmi,dia_cmi,hora_cmi,minuto_cmi,fechaArch_cmi = fecha(cmi_data)  
    
    plt.text(235000,1734173,'GOES-16/ABI   '+fechaG16_cmi+' GMT',fontsize=20,fontname = 'gadugi',color='white')
    plt.text(235000,1634173,'GOES-16/GLM '+fechaG16+' GMT',fontsize=20,fontname = 'gadugi',color='white')
        
    cmi_ = Dataset(cmi_data,'r')

# ====================================================================
# TEMPORAL Radiancia a Refletancia 

   #planck_fk1 = cmi_.variables['planck_fk1'][:]
   #planck_fk2 = cmi_.variables['planck_fk2'][:]
   #planck_bc1 = cmi_.variables['planck_bc1'][:]
   #planck_bc2 = cmi_.variables['planck_bc2'][:]
    
    cmi = cmi_.variables['CMI'][:]     
    
    #cmi = (planck_fk2 / (np.log((planck_fk1 / cmi)+ 1)) - planck_bc1) / planck_bc2 

# ===================================================================

    logo = plt.imread('/home/lanotadm/data/logos/LANOT2.png')
    
    plt.figimage(logo,20,1550,zorder=2,origin = 'upper')   
    
    #plt.imshow(cmi,extent=[-3627271.3409673548303545,1382771.9477514973841608,1583173.7916531809605658,4589199.7648844923824072],cmap='Greys' ,vmin=250)
    plt.imshow(cmi,extent=[-3637271.3409673548303545,1382771.9477514973841608,1583173.7916531809605658,4559199.7648844923824072],cmap='Greys',vmin=50)
            
    plt.savefig('/data1/output/glm/images/conus/'+i[i.find('OR_'):-3]+'.jpg',bbox_inches='tight', pad_inches=0)
    
    image = Image.open('/data1/output/glm/images/conus/'+i[i.find('OR_'):-3]+'.jpg')
    image = image.crop((10,10,image.width-10,image.height-10))
    image.save('/data1/output/glm/images/conus/'+i[i.find('OR_'):-3]+'.jpg')

    image = None
    cmi = None
    cmi_ = None
    lat,lon,area,energy,quality,id_var = None,None,None,None,None,None
    glm = None      
    #fechaStr,fechaG16,ano,dia,hora,minuto,fechaArch = None
    archivo = None 
    #ax = None
    coastlines = None       
    shpMuni = None
    x,y = None,None
    
    plt.clf()
    plt.cla() 
    plt.gca()
    plt.gcf()
    ax.clear()
    plt.close()

eleapsed_time = time() - start
print ("Tiempo de ejecucion: %.10f segundos"%eleapsed_time)

        #
