#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 14:11:34 2019

@author: lanot
"""

import glob
import os
from time import strptime,strftime

def copiaNetCDF():
    os.system('sh /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/NetCDFGOES16.sh')

def revisaNetCDF():
    files = glob.glob('/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_GOES16/LST/*.nc')    
    fecha = files[0][files[0].find('_c')+2:files[0].find('.nc')-3]
    fechaG16 = strftime("%Y/%m/%d %H:%M",strptime(fecha,"%Y%j%H%M%S"))
    tiempoG16 =  float(fechaG16[11:13]+fechaG16[14:])
    #print fechaG16 
    #print 'Descargado:',files
    #print "Fecha:",fechaG16
    
    return fechaG16,tiempoG16

def borraNetCDF(): 
    os.system('rm /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_GOES16/LST/*')

def extraeNetCDF(): 
    print 'Copiando LST NetCDF'    
    copiaNetCDF()
    return 

#extraeNetCDF()
#print revisaNetCDF()
#borraNetCDF()