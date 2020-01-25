#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 18:29:42 2020

@author: urielm
"""

from osgeo import gdal,osr
import numpy as np
#import matplotlib.pyplot as plt
import os
from glob import glob

def rebin(a, shape):
    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)

def normaliza(data):
    print ('Normalizando dato...')   
    data = (data - np.nanmin(data))*255/(np.nanmax(data)-np.nanmin(data))    
    return data

def rescala(data, start, end):
    width = end - start
    data = (data - np.nanmin(data))/(np.nanmax(data) - np.nanmin(data)) * width + start
    return data

def compuestoRGB(r,g,b,entero):
    print ('Creando compuesto RGB...') 
    if entero == True:
        rgb = (np.dstack((r,g,b))).astype('uint8') 
    else:
        rgb = (np.dstack((r,g,b)))
    return rgb

def creaTiff(data, ds, nombre):
    print ('Creando tif...')   
    
    geotransform = ds.GetGeoTransform()
    
    # Parametros para la creacion del TIFF por medio de GDAL
    nx = data.shape[1]
    ny = abs(data.shape[0])
    dst_ds = gdal.GetDriverByName('GTiff').Create(nombre+'.tif', nx, ny, 1, gdal.GDT_Float32)
    
    # Aplica la geotransformacion y la proyección
    dst_ds.SetGeoTransform(geotransform)    # Coordenadas especificas
    srs = osr.SpatialReference()            # Establece el ensamble
    srs.ImportFromWkt(ds.GetProjectionRef())
    dst_ds.SetProjection(srs.ExportToWkt()) # Exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data) # Escribe la banda al raster
    dst_ds.FlushCache()                     # Escribe en el disco
    
    dst_ds = None

    
def extrae(path):
    ds = gdal.Open(path)
    data = ds.ReadAsArray()
    
    return ds,data

def ftVIIRS(r,g,b,rango):
    # Apply range limits or each channel (mostly important for Red channel)
    #r = np.maximum(r, 325)
    #r = np.minimum(r, 305)    
    #g = np.maximum(g, 0)
    #g = np.minimum(g, 1)
    #b = np.maximum(b, 0)
    #b = np.minimum(b, .75)
    
    # Normalize each channel by the appropriate range of values (again, mostly important for Red channel)
    #r = ((r-305)/(325-305))*325
    #g = (g-0)/(1-0)
    #b = (b-0)/(.75-0)
  
    # Umbral del valores del rojo 305 a 315

     
    rmask = r
    rmask = np.where(np.isnan(rmask) == True,np.nan,1)

        
    r = np.where(r <= rango[0] ,rango[0],r)
    r = np.where(r >= rango[1],rango[1],r)
    
    g = np.where(g <= 0 ,0,g)
    g = np.where(g >= 1 ,1,g)
    
    b = np.where(b <= 0 ,0,b)
    b = np.where(b >= 0.75 ,0.75,b)
    #r = np.where(r > 325,324,r)
    
    #r = rescala(r,rango[0],rango[1])

    #r = rescale_linear(r,305,325)
    #r = (r - np.nanmin(r))*325/(np.nanmax(r)-np.nanmin(r)*305) + 305 
    
    # Apply the gamma correction to Red channel.
    #   I was told gamma=0.4, but I get the right answer with gamma=2.5 (the reciprocal of 0.4)
    #r = np.power(r,2)
    


    r = normaliza(r).astype('uint8') 
    #r = rescala(r,0,130).astype('uint8') 
    g = normaliza(g).astype('uint8') 
    b = normaliza(b).astype('uint8') 
        
    r = r*rmask
    g = g*rmask
    b = b*rmask
    
    #r = np.where(np.isnan(r) == True , np.nan,r)
    #g = np.where(np.isnan(g) == True , np.nan,g)
    #b = np.where(np.isnan(b) == True , np.nan,b)
        
    print(r)
    print(g)
    print(b)
   
    return r,g,b,rmask
    

def creaTiffPaso2(path12,path11,path10,paso):
    ds12,r = extrae(path12[paso])
    ds11,g = extrae(path11[paso])
    ds10,b = extrae(path10[paso])
        
    r,g,b,rmask = ftVIIRS(r,g,b,(305,325))
    
    creaTiff(r, ds12, 'R'+str(paso+1))
    creaTiff(g, ds11, 'G'+str(paso+1))
    creaTiff(b, ds10, 'B'+str(paso+1))

def recortaPaso2(banda,paso):
    
    xmin = -118
    xmax = -85
    ymin = 12
    ymax = 33.5
    lonUnion = -94.5
    
    if paso == 1:
        os.system('gdal_translate -projWin '+str(xmin)+' '+str(ymax)+' '+str(lonUnion)+' '+str(ymin)+' '+banda+'.tif '+banda+'_rec.tif')
    elif paso == 2:
        os.system('gdal_translate -projWin '+str(lonUnion)+' '+str(ymax)+' '+str(xmax)+' '+str(ymin)+' '+banda+'.tif '+banda+'_rec.tif')

def unionPaso2(banda):
    
    os.system('gdal_merge.py -o '+banda+'.tif '+banda+'2_rec.tif '+banda+'1_rec.tif')

def borra(paso):
    tempRGB = ('R','G','B')    
    for i in tempRGB:
        temp = glob('./'+i+'*.tif')
        for j in temp:
            os.remove(j)
    if paso == 1:
        os.remove('rgb.tif')
    
def paso2(path12,path11,path10,pathOutput,salida):
    
    creaTiffPaso2(path12,path11,path10,0)
    creaTiffPaso2(path12,path11,path10,1)
     
    recortaPaso2('R1',1)
    recortaPaso2('G1',1)
    recortaPaso2('B1',1)
    
    recortaPaso2('R2',2)
    recortaPaso2('G2',2)
    recortaPaso2('B2',2)
    
    unionPaso2('R')
    unionPaso2('G')
    unionPaso2('B')
    
    os.system('gdal_merge.py -separate -co PHOTOMETRIC=RGB -o '+pathOutput+salida+' R.tif G.tif B.tif')
    
def recortaPaso1(salida):
    
    xmin = -118
    xmax = -85
    ymin = 12
    ymax = 33.5
    
    os.system('gdal_translate -projWin '+str(xmin)+' '+str(ymax)+' '+str(xmax)+' '+str(ymin)+' rgb.tif '+pathOutput+salida)

def paso1(path12,path11,path10,pathOutput,salida):
    ds12,r = extrae(path12)
    ds11,g = extrae(path11)
    ds10,b = extrae(path10)
        
    r,g,b,rmask = ftVIIRS(r,g,b,(310,325))
    
    creaTiff(r, ds12, 'R')
    creaTiff(g, ds11, 'G')
    creaTiff(b, ds10, 'B')
    
    #rgb = compuestoRGB(r,g,b,True)
    
    #plt.figure(figsize=(20,20))
    #plt.imshow(rgb)
    
    os.system('gdal_merge.py -separate -co PHOTOMETRIC=RGB -o rgb.tif R.tif G.tif B.tif')
    
    recortaPaso1(pathOutput,salida)
    
    return 

def comparaPaso(path,banda):
    archivos = glob(path+'*'+banda+'*')
    archivos.sort()
    
    ultimo = archivos[-1]
    penultimo = archivos[-2]
    
    print(ultimo)
    
    diaU = ultimo.split('/')[-1].split('_')[3]    
    horaU = ultimo.split('/')[-1].split('_')[4]
    
    diaP = penultimo.split('/')[-1].split('_')[3]   
    horaP = penultimo.split('/')[-1].split('_')[4]
    
    if diaU != diaP:
        print(diaU,horaU)
        print(diaP,horaP)
        return 1
    elif diaU == diaP and horaU != horaP:
        print(diaU,horaU)
        print(diaP,horaP)
        return 2
    else:
        return False

def extraeArchivo(path,banda,paso):
    archivos = glob(path+'*'+banda+'*')
    archivos.sort()
    
    if paso == 1:
        archivo = archivos[-1]
        
        salida = archivo.split('/')[-1].split('_')
        salida[2] = 'FT'
        salida = '_'.join(map(str,salida))        
        return archivo,salida
    elif paso ==2:
        archivo1 = archivos[-1]
        archivo2 = archivos[-2]
        
        salida = archivo1.split('/')[-1].split('_')
        salida[2] = 'FT'
        salida = '_'.join(map(str,salida))        
        
        return archivo1,archivo2,salida
    
    
pathInput = '/home/urielm/Documents/LANOT_CENAPRED/ver2/compuestos/datos/viirs/'
pathOutput = ''

paso = comparaPaso(pathInput,'m10')

if paso == 1:
    print('1 PASO VIIRS..')
    b10,salida = extraeArchivo(pathInput,'m10',paso)
    b11,salida = extraeArchivo(pathInput,'m11',paso)
    b12,salida = extraeArchivo(pathInput,'m12',paso)
    
    paso1(b12,b11,b10,pathOutput,salida)
    borra(paso)

elif paso == 2:
    print('2 PASOS VIIRS..')
    b10_1,b10_2,salida = extraeArchivo(pathInput,'m10',paso)    
    b11_1,b11_2,salida = extraeArchivo(pathInput,'m11',paso)
    b12_1,b12_2,salida = extraeArchivo(pathInput,'m12',paso)
    
    b10 = [b10_1,b10_2]
    b11 = [b11_1,b11_2]
    b12 = [b12_1,b12_2]
    
    paso2(b12,b11,b10,pathOutput,salida)
    borra(paso)
    
else:
    print('No hay archivos')
