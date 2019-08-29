#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 15:58:28 2019

@author: lanot
"""

import glob
import os
from time import strptime,strftime


def copiaGTif():
    os.system('sh /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/GeoTiffSuomiNPP.sh')

def revisaGTif(paso):
    files = glob.glob('/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_SuomiNPP/SST/*')
    if paso == 1:
        fecha = files[0][files[0].find('/2019')+1:files[0].find('.npp')]
    else:
        fecha = files[2][files[2].find('/2019')+1:files[2].find('.npp')]

    fechaSNPP = strftime("%Y/%m/%d %H:%M",strptime(fecha,"%Y.%m%d.%H%M"))
    tiempoSNPP = float(fechaSNPP[11:13]+fechaSNPP[14:])
    fechaSNPP = fechaSNPP[:10]

    print 'Descargado:',files
    print "Fecha:",fechaSNPP
    print "Hora:",tiempoSNPP

    return fechaSNPP,tiempoSNPP

def borraGTif(): 
    os.system('rm /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_SuomiNPP/SST/*')

def extraeGTiff():        
    print 'Copiando SST GeoTIFF'    
    copiaGTif()
    return 

#revisaGTif(2)
#extraeGTif()
#borraGTif()
