#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 17:46:29 2019

@author: lanot
"""

from netCDF4 import Dataset
import GOES16 as G16
import glob
import os
from osgeo import gdal
from pyproj import Proj,transform
import numpy as np
#import matplotlib.pyplot as plt
from datetime import datetime

archivos = glob.glob('./*OR*.nc')
archivos.sort()

fechaInicio = datetime.strptime(archivos[0][archivos[0].find('_s')+2:archivos[0].find('_s')+15],'%Y%j%H%M%S')
fechaFinal = datetime.strptime(archivos[-1][archivos[-1].find('_s')+2:archivos[-1].find('_s')+15],'%Y%j%H%M%S')

eventoMeteo = 'Tropical'
region = 'Atlántico'
nomEvento = 'katia'

evento = Dataset("katia.nc",'w')

evento.naming_authority = 'gov.nesdis.noaa'
evento.Conventions = 'CF-1.7'
evento.Metadata_Conventions = 'Unidata Dataset Discovery v1.0'
evento.standard_name_vocabulary = 'CF Standard Name Table (v25, 05 July 2013)'
evento.institution = 'UNAM/LANOT/CCUD > Universidad Nacional Autónoma de México, Laboratorio Nacional de Observación de la Tierra , Coordinación de Colecciones Universitarias Digitales '  
evento.project  = 'Colección de eventos meteorológicos'
evento.production_site = 'LANOT'
evento.spatial_resolution = '2km al nadir'   
evento.orbital_slot = 'GOES-Test'
evento.platform_ID = 'G16'
evento.instrument_type = 'GOES R Series Advanced Baseline Imager'
evento.scene_id = region
evento.instrument_ID = 'FM1'
evento.dataset_name = nomEvento+'.nc' 
evento.title = 'Evento metrológico, '+fechaInicio.strftime("%Y")+', '+eventoMeteo+', '+region+', '+nomEvento.capitalize()+', ABI L2 Cloud and Moisture Imagery'
evento.summary = 'Conjunto de datos del producto Cloud and Moisture Imagery de la banda 14 del sensor Advanced Baseline Imager de GOES R Series. El producto son mapas digitales de nubes, humedad y ventanas atmosféricas en bandas del Infra-Rojo'
evento.license = 'Datos sin clasificar'
evento.processing_level = 'National Aeronautics and Space Administration (NASA) L2'
evento.date_created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
evento.cdm_data_type = 'Imagen'
evento.time_coverage_start = fechaInicio.strftime("%Y-%m-%dT%H:%M:%SZ")
evento.time_coverage_end = fechaFinal = fechaFinal.strftime("%Y-%m-%dT%H:%M:%SZ")
evento.timeline_id = 'A cada 1 hr'
evento.production_data_source = 'Tiempo real'
evento.id = 'EM-'+eventoMeteo[0]+'-'+fechaInicio.strftime("%Y")+'-'+region[0]+'-'+nomEvento.capitalize()

evento.createDimension('lon',2003)
evento.createDimension('lat',1031)
evento.createDimension('time',None)
evento.createDimension('nv',2)

lon = evento.createVariable('lon',np.float32,('lon',))
lon.units = 'grados_Este'
lon.long_name = 'longitud'
lon.standard_name = 'longitud'
lon.axis = 'X'
lon.vertices = 'lon_vertices'

lat = evento.createVariable('lat',np.float32,('lat',))
lat.units = 'grados_Norte'
lat.long_name = 'latitud'
lat.standard_name = 'latitud'
lat.axis = 'Y'
lat.vertices = 'lat_vertices'

time = evento.createVariable('time',np.float32,('time',))
# 'hours since 2017-9-5 00:00:00'
time.units = 'hours since '+fechaInicio.strftime("%Y-%m-%d %H:%M:00") 
time.long_name = 'time'
time.axis = 'T'
time.calendar = 'gregorian'

cmi = evento.createVariable('CMI',np.float32,('time','lat','lon'))
cmi.units = 'grados_Celsius'
cmi.long_name = 'ABI L2+ Cloud and Moisture Imagery brightness temperature'
cmi.standard_name = 'toa_brightness_temperature'
cmi.coordinates = 'lat lon'
#cmi.grid_mapping = ""
cmi.setncattr('grid_mapping', 'spatial_ref')

lon_vertices = evento.createVariable('lon_vertices',np.float32,('nv'))
lon_vertices.units = 'grados_Este'
lon_vertices.long_name = 'Coordenadas en X oeste/este de la extensión de la imagen'
lon_vertices.standard_name = 'vertices_longitud'

lat_vertices = evento.createVariable('lat_vertices',np.float32,('nv'))
lat_vertices.units = 'grados_Norte'
lat_vertices.long_name = 'Coordenadas en Y sur/norte de la extensión de la imagen'
lat_vertices.standard_name = 'vertices_latitud'

crs = evento.createVariable('spatial_ref', 'i4')
crs.grid_mapping_name = 'latitude_longitude'
crs.longitude_of_prime_meridian = 0.0
crs.semi_major_axis = 6378137.0
crs.inverse_flattening = 298.257223563
crs.geographic_coordinate_system_name = "WGS 84"
crs.horizontal_datum_name = "WGS_1984"
crs.reference_ellipsoid_name = "WGS 84"
crs.spatial_ref = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'


#coor = [-2694149,3755481,3370602,198271]
coor = [-135,45,-15,-20]

p1 = Proj("+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-89.5 +sweep=x +no_defs")
p2 = Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

xmin,ymin = transform(p2,p1,coor[0],coor[3])
xmax,ymax = transform(p2,p1,coor[2],coor[1])

coor = [xmin,ymax,xmax,ymin]

coor2 = [-120,36,-52,1]
#xmin,ymin = transform(p1,p2,coor[0],coor[3])
#xmax,ymax = transform(p1,p2,coor[2],coor[1])

time_cont = 0

#lon_vertices[:] = [-120.0137724,-52.0107142]
#lat_vertices[:] = [1.0048826,36.0079545]

for i in archivos:    
    print('Archivo:' + i)   
    
    data, xmin, ymin, xmax, ymax, nx, ny = G16.extraeNetCDFL2(i)    
    #print data, xmin, ymin, xmax, ymax, nx, ny
    
    G16.creaTiff(data, xmin, ymin, xmax, ymax, nx, ny)
    
    ds = gdal.Open('tmp.tif') 
    
    gdal.Translate('tmp_rec.tif',ds,options = gdal.TranslateOptions(projWin=coor))
    
    ds = gdal.Open('tmp_rec.tif') 
    
    gdal.Warp('tmp_rec_4326.tif',ds,options=gdal.WarpOptions(dstSRS='EPSG:4326',dstNodata=-9999.000))
    
    ds = gdal.Open('tmp_rec_4326.tif')
    
    gdal.Translate('tmp_rec_4326_rec.tif',ds,options = gdal.TranslateOptions(projWin=coor2))
    
    ds = gdal.Open('tmp_rec_4326_rec.tif')
    
    data = ds.ReadAsArray()
            
    data = data - 273.15
         
    data[data == -9999.0] = np.nan
    #data[data >= 0.0] = np.nan
    
    #np.flipud(data)    
        
    print ('Añadiendo archivo '+str(time_cont)+':'+i)
    
    #x[:] = temp_nc.variables['x'][500:3500]
    #y[:] = temp_nc.variables['y'][500:2500]
    
    temp_cmi = np.flipud(data)

    #tem_x = temp_nc.variables['x'][500:3500]
    #tem_y = temp_nc.variables['x'][500:3500]
    
    cmi[time_cont:time_cont+1,:,:] = temp_cmi
    time[time_cont] = time_cont
    time_cont = time_cont + 1
    
    #plt.imshow(data)
    #plt.savefig(str(time_cont)+'.jpg')
    #plt.show()
    
    os.remove('tmp.tif')
    os.remove('tmp_rec.tif')
    os.remove('tmp_rec_4326.tif')
    
    #os.remove('tmp_rec_4326_rec.tif')

#evento.close()

#evento = Dataset("katia.nc",'a')

#os.system('gdal_translate NETCDF:'+nomEvento+'.nc:CMI '+nomEvento+'.tif')

ds = gdal.Open('tmp_rec_4326_rec.tif')

resx = ds.GetGeoTransform()[1]
resy = ds.GetGeoTransform()[5]

lonVert_min = ds.GetGeoTransform()[0]
lonVert_max = ds.GetGeoTransform()[0]+resx*(data.shape[1])
latVert_min = ds.GetGeoTransform()[3]+resy*(data.shape[0])
latVert_max = ds.GetGeoTransform()[3]

coor2 = [-120,36,-52,1]
evento.variables['lon'][:] =  np.linspace(lonVert_min,lonVert_max,2003)
evento.variables['lat'][:] =  np.linspace(latVert_min,latVert_max,1031)

evento.variables['CMI'].resolution ='lat:'+str(resy)+' grados lon:'+str(resx)+' grados'
evento.variables['lon_vertices'][:] = [lonVert_min,lonVert_max]
evento.variables['lat_vertices'][:] = [latVert_min,latVert_max]
    
evento.close()

os.remove('tmp_rec_4326_rec.tif')