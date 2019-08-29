#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 15:58:28 2019

@author: lanot
"""

import glob
import os
from time import strptime,strftime


def copiaGTif(banda):
    os.system('sh /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/GeoTiffSuomiNPP.sh '+banda)

def revisaGTif(banda,paso):
    files = glob.glob('/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_SuomiNPP/C'+banda+'/*.'+paso+'*.npp*.tif')  
    fecha = files[0][files[0].find('/2019')+1:files[0].find('.npp')]
    fechaSNPP = strftime("%Y/%m/%d %H:%M",strptime(fecha,"%Y.%m%d.%H%M"))
    print 'Descargado:',files
    print "Fecha:",fechaSNPP
    
    return fechaSNPP

def borraGTif(banda): 
    os.system('rm /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_SuomiNPP/C'+banda+'/*')

def borraTodo():
    print 'Borrando GTiff'
    for i in range(12):
        if 2 < i+1 < 6:
            borraGTif('0'+str(i+1))
        if 9 < i+1 < 13:
            borraGTif(str(i+1))

def extraeGTiff():    

    print 'Copiando BT HDF5'
    for i in range(12):
        if 2 < i+1 < 6:
            copiaGTif('0'+str(i+1))       
        if 9 < i+1 < 13:
            copiaGTif(str(i+1))
    return 

#revisaGTif('03','18')
#extraeGTiff()
#borraTodo()
