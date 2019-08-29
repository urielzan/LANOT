#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 13:33:32 2019

@author: lanot
"""

import matplotlib
matplotlib.use('Agg')
import dataGOES16,dataSuomiNPP,dataSentinel2

import GOES16,SuomiNPP,Sentinel2

import ensambleCoor

import os
#import sys
path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/'

pathPuntosCalor = path+'data_PuntosCalor/'
pathGOES16 = path+'data_GOES16/'
pathSuomiNPP = path+'data_SuomiNPP/'
pathSentinel2 = path+'data_Sentinel2/'

#x = -99.7675
#y = 19.101666666667
x = -99.1329
y = 19.433248

dataGOES16.extraeNetCDF()
dataSuomiNPP.extraeGTiff()

print "\nProcesando Coordenada: ",x,',',y

offsetGOES16 = 1
offsetSuomiNPP = 0.5
offsetSentinel2 = 0.1

dataSentinel2.extraeWMS(x,y,offsetSentinel2,'1-NATURAL-COLOR,DATE','TC_',pathSentinel2,'TC')
dataSentinel2.extraeWMS(x,y,offsetSentinel2,'2_COLOR_INFRARED__VEGETATION_,DATE','SWIR_',pathSentinel2,'SWIR')

G16_TC_imagen,G16_FT_imagen = GOES16.RGBGoes16(pathGOES16,x,y,offsetGOES16)
SNPP_TC_imagen,SNPP_FT_imagen,paso = SuomiNPP.RGBSuomiNPPI(pathSuomiNPP,x,y,offsetSuomiNPP)
Sen2_TC_imagen = Sentinel2.RGBSentilen2(x,y,offsetSentinel2,'TC',pathSentinel2,'Sentinel2_TC_')
Sen2_SWIR_imagen = Sentinel2.RGBSentilen2(x,y,offsetSentinel2,'SWIR',pathSentinel2,'Sentinel2_SWIR_')

fechaG16 = dataGOES16.revisaNetCDF('1')
if paso == 1:        
    fechaSNPP = dataSuomiNPP.revisaGTif('03','19')
else:
    fechaSNPP = dataSuomiNPP.revisaGTif('03','18')
    
logo_path = 'logo.jpg'
ubiMun_path = 'ubicacion_muni.png'
ubiEnt_path = 'ubicacion_edo.png'
ensambleCoor.ensambleSat(x,y,G16_TC_imagen,G16_FT_imagen,SNPP_TC_imagen,SNPP_FT_imagen,Sen2_TC_imagen,Sen2_SWIR_imagen,ubiMun_path,ubiEnt_path,logo_path,fechaG16,fechaSNPP)

os.remove(G16_TC_imagen)
os.remove(G16_FT_imagen)
os.remove(SNPP_TC_imagen)
os.remove(SNPP_FT_imagen)
#os.remove(Sen2_TC_imagen)
#os.remove(Sen2_SWIR_imagen)
os.remove('ubicacion_edo.png')
os.remove('ubicacion_muni.png')
os.remove('tmp_rec.tif.aux.xml')
os.remove('tmp_4326_rec.tif.aux.xml')

dataGOES16.borraTodo()
dataSuomiNPP.borraTodo()
dataSentinel2.borraTodo()

