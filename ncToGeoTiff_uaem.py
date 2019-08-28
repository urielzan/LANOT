#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:35:37 2019

@author: lanot
"""

import os
#from osgeo import gdal#,osr
import sys
import pandas as pd
from glob import glob
from datetime import datetime

def archivoNC(path,var):
    
    nc = glob(path+'/*'+var.upper()+'*.nc')
    nc.sort()
    nc = nc[-1] 
    
    return nc  

def dateG16(path):
    
    date = datetime.strptime(path[path.find('_s')+2:path.find('_s')+15],'%Y%j%H%M%S')
    date = date.strftime("%Y.%m%d.%H%M")
    
    return date

def ncToGeotiff(pathInput,pathOutput,proc,var,epsg,res,master):
    
        nc = archivoNC(pathInput,var)
        
        date = dateG16(nc)
        
        os.system('gdal_translate -of GTiff -ot float32 -unscale NETCDF:'+nc+':'+var.upper()+' /var/tmp/recortes/tmp_'+var+'_uaem.tif')
        
        os.system('gdalwarp -overwrite -CO COMPRESS=deflate -t_srs EPSG:'+epsg+' /var/tmp/recortes/tmp_'+var+'_uaem.tif /var/tmp/recortes/master_'+var+'_uaem.tif')   
         
        os.system('gdal_calc.py -A /var/tmp/recortes/master_'+var+'_uaem.tif --outfile=/var/tmp/recortes/master_'+var+'_mod_uaem.tif --calc="A - 273.15" --NoDataValue=-9999.0')
        
        for i in master:       
            
            df = pd.read_csv('/home/lanotadm/doc/recortes_coordenadas.csv')
	    
	    #print (df)
            ul_x = str(float(df[df['clave'] == i ]['ul_x'].values))
            ul_y = str(float(df[df['clave'] == i ]['ul_y'].values))
            lr_x = str(float(df[df['clave'] == i ]['lr_x'].values))
            lr_y = str(float(df[df['clave'] == i ]['lr_y'].values))
            
            os.system('gdalwarp -overwrite -te '+ul_x+' '+lr_y+' '+lr_x+' '+ul_y+' /var/tmp/recortes/master_'+var+'_mod_uaem.tif '+pathOutput+'/'+i+'/celsius/goes16.abi-'+date+'-'+proc+'_'+var+'_'+res+'.tif')
        
        os.remove('/var/tmp/recortes/tmp_'+var+'_uaem.tif')
        os.remove('/var/tmp/recortes/master_'+var+'_mod_uaem.tif')
        
        #os.system('mv /var/tmp/recortes/master_'+var+'.tif '+pathOutput+'/fd/goes16.abi-'+date+'-'+var+'_'+res+'.tif')
        
        os.remove('/var/tmp/recortes/master_'+var+'_uaem.tif')

pathInput = sys.argv[1]
pathOutput = sys.argv[2]

#nc = 'CG_ABI-L2-LSTF-M6_G16_s20192322030203_e20192322039523_c20192321553300.nc'
#prc = 'LST'
#epsg = '4326'

proc = sys.argv[3]
var = sys.argv[4]
epsg = sys.argv[5]
res = sys.argv[6]
master = sys.argv[7].split(',')

print('pathInput: '+pathInput)
print('pathOutput: '+pathOutput)
print('var: '+var)
print('epsg: '+epsg)
print('res: '+res)
print('master: ',master)

ncToGeotiff(pathInput,pathOutput,proc,var,epsg,res,master)


