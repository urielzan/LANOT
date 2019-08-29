#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 14:11:34 2019

@author: lanot
"""

import glob
import os
from time import strptime,strftime

def copiaNetCDF(banda):
    os.system('sh /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/NetCDFGOES16.sh '+banda)

def revisaNetCDF(banda):
    files = glob.glob('/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_GOES16/C0'+banda+'/*.nc')    
    fecha = files[0][files[0].find('_c')+2:files[0].find('.nc')-3]
    fechaG16 = strftime("%Y/%m/%d %H:%M",strptime(fecha,"%Y%j%H%M%S"))
    #print fechaG16 
    #print 'Descargado:',files
    #print "Fecha:",fechaG16
    
    return fechaG16

def borraNetCDF(banda): 
    os.system('rm /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_GOES16/C0'+banda+'/*')

def borraTodo():
    print 'Borrando CMI NetCDFs'
    for i in range(7):
        if i+1 != 4:     
            borraNetCDF(str(i+1))

def extraeNetCDF():    

    print 'Copiando CMI NetCDF'
    for i in range(7):
        if i+1 != 4:
            copiaNetCDF(str(i+1))       
       
    return 

#revisaNetCDF('1')
#extraeNetCDF()
#borraTodo()
