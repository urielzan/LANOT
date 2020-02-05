#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 17:21:12 2020

@author: urielm
"""


#from osgeo import gdal,osr
#import numpy as np
#import matplotlib.pyplot as plt
import os
from glob import glob


def comparaPaso(path):
    archivos = glob(path+'*CVIIRSM*')
    archivos.sort()
    
    ultimo = archivos[-1]
    penultimo = archivos[-2]
    
    print(ultimo)
    
    diaU = ultimo.split('/')[-1].split('_')[1].split('.')[-1][1:]
    #diaUs = diaU[:4]+'-'+diaU[4:6]+'-'+diaU[6:]
    horaU = ultimo.split('/')[-1].split('_')[2].split('.')[-1][1:]
    #horaUs = horaU[:2]+':'+horaU[2:4]+':'+horaU[4:]
    
    diaP = penultimo.split('/')[-1].split('_')[1].split('.')[-1][1:]
    #diaPs = diaP[:4]+'-'+diaP[4:6]+'-'+diaP[6:]
    horaP = penultimo.split('/')[-1].split('_')[2].split('.')[-1][1:]
    #horaPs = horaP[:2]+':'+horaP[2:4]+':'+horaP[4:]
    
    print(diaU,horaU)
    print(diaP,horaP)

    if diaU != diaP:
        #print(diaU,horaU)
        #print(diaP,horaP)
        return 1
    elif diaU == diaP and horaU != horaP :
        #print(diaU,horaU)
        #print(diaP,horaP)
        #print('Resta:',int(horaU)-int(horaP))
        return 2
    else:
        return False


def extraeArchivo(path,paso):
    archivos = glob(path+'*CVIIRSM*')
    archivos.sort()
    
    if paso == 1:
        archivo = archivos[-1]       
     
        return archivo
    elif paso ==2:
        archivo1 = archivos[-1] 
        archivo2 = archivos[-2] 
        
        return archivo1,archivo2

def recortaPaso1(pathInput,pathOutput,salida):
    
    xmin = -118
    xmax = -85
    ymin = 12
    ymax = 33.5
    
    os.system('gdal_translate -projWin '+str(xmin)+' '+str(ymax)+' '+str(xmax)+' '+str(ymin)+' '+pathInput+' '+pathOutput+salida)    

def paso1(pathInput,pathOutput,salida):
    archivo = extraeArchivo(pathInput,1)
    recortaPaso1(archivo,pathOutput,salida+'.tif')
      

def borra(salida):
    os.remove(salida+'.tif') 
        
def recortaPaso2(pathInput,salida,paso):
    
    xmin = -118
    xmax = -85
    ymin = 12
    ymax = 33.5
    lonUnion = -94.5
    
    if paso == 1:
        os.system('gdal_translate -projWin '+str(xmin)+' '+str(ymax)+' '+str(lonUnion)+' '+str(ymin)+' '+pathInput+' '+salida+'_rec.tif')
    elif paso == 2:
        os.system('gdal_translate -projWin '+str(lonUnion)+' '+str(ymax)+' '+str(xmax)+' '+str(ymin)+' '+pathInput+' '+salida+'_rec.tif')

def unionPaso2(pathOutput,salida):
    
    os.system('gdal_merge.py -o '+pathOutput+salida+'.tif '+salida+'_2_rec.tif '+salida+'_1_rec.tif')

def paso2(pathInput,pathOutput,salida):
         
    archivo1,archivo2 = extraeArchivo(pathInput,2)
    recortaPaso2(archivo1,salida+'_1',1)    
    recortaPaso2(archivo2,salida+'_2',2) 
    
    unionPaso2(pathOutput,'viirs_TC_latest')

def viirsTC(pathInput,pathOutput):
    paso = comparaPaso(pathInput)
 	
    print(paso)   

    if paso == 1:
        paso1(pathInput,pathOutput,'viirs_TC_latest')
    
    elif paso == 2:
        paso2(pathInput,pathOutput,'viirs_TC_latest')
        borra('viirs_TC_latest_1_rec')
        borra('viirs_TC_latest_2_rec')
    else:
        print('No hay archivos')
    
pathInput = '/data2/output/polar/jpss1/viirs/level2/vistas/cviirs/'
pathOutput = '/data2/tmp/latest/'

viirsTC(pathInput,pathOutput)
