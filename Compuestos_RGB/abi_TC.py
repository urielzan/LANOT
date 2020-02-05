#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 12:52:43 2020

@author: urielm
"""

from osgeo import gdal,osr
import numpy as np
import os
from glob import glob

def revisaFecha(path):
    archivos = glob(path+'*goes-16.rgb*')
    archivos.sort()
    
    ultimo = archivos[-1]
    
    print(ultimo)
    
    diaU = '-'.join(map(str,ultimo.split('/')[-1].split('.')[:3]))
    horaU = ':'.join(map(str,ultimo.split('/')[-1].split('.')[3:5]))
        
    print(diaU)
    print(horaU)

    return ultimo,diaU,horaU

def reproyecta(path):
    os.system('gdalwarp -t_srs EPSG:4326 '+path+' tmp_geo.tif')
    
def recortaCONUS(pathOutput):    
    xmin = -118
    xmax = -85
    ymin = 15
    ymax = 33.5
    
    os.system('gdal_translate -projWin '+str(xmin)+' '+str(ymax)+' '+str(xmax)+' '+str(ymin)+' tmp_geo.tif '+pathOutput+'abi_TC_latest.tif')

def borra():
    os.remove('tmp_geo.tif')    

def abiTC(pathInput,pathInput2,pathOutput):    
    ultimo,diaU,horaU = revisaFecha(pathInput)
    reproyecta(pathInput2)
    recortaCONUS(pathOutput)
    borra()
    
pathInput = '/data/goes16/abi/vistas/rgb/conus/'
pathInput2 = '/var/tmp/rgbconus/tmp.tif'
pathOutput = '/data2/tmp/latest/'

abiTC(pathInput,pathInput2,pathOutput)
