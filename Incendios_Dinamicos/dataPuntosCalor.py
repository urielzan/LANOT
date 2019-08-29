#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 13:17:05 2019

@author: lanot
"""
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import cartopy.crs as crrs
import matplotlib.pyplot as plt
import glob
import os
import time as tm
from time import strptime,strftime

def copiaCSV():
    os.system('sh /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/CSVPuntosCalor.sh')

def revisaCSV():
    files = glob.glob('/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_PuntosCalor/*.csv')    
    fecha = files[0][files[0].find('_2019')+1:files[0].find('.csv')]
    print 'Descargado:',files,"Fecha:",tm.strftime("%Y/%m/%d %H:%M",tm.strptime(fecha,"%Y%j%H%M%S"))

def borraCSV(): 
    os.system('rm /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_PuntosCalor/*')

def archivoCSV(path):
    csv = os.listdir(path)[0]
    
    return csv


def plotPuntos(x,y):
    
    plt.figure(figsize=(10,10))
    ax = plt.axes(projection=crrs.PlateCarree())
    ax.coastlines()
    
    plt.plot(x,y,'r.')
    
def dataCSV(csv):
    
    df = pd.read_csv(csv)    
    
    puntos = len(df.axes[0])
    #elem = len(df.axes[0][1])
    
    x = []
    y= []
    tiempoIni = []
    tiempoTer = []
    
    csvArchivo = csv[csv.find('Calor/')+6:]
    fechaPC = csvArchivo[csvArchivo.find('unam_')+5:csvArchivo.find('.csv')]
    fechaPC = strptime(fechaPC,'%Y%m%d%H%M')   
    fechaPC = strftime("%Y-%m-%d %H:%M",fechaPC)
    
    for i in range(puntos):
        data = df.axes[0][i]
        if data[1] != 'longitude' and (-122.19 < float(data[1]) < -84.64) and (12.53< float(data[0]) < 32.72):
            x.append(float(data[1]))
            y.append(float(data[0]))
            tiempoIni.append(data[2])
            tiempoTer.append(data[3])
    
    puntosMexico = len(x)
        
    print("Archivo CSV: "+csvArchivo)
    print("Tiempo: ",fechaPC)
    print ("Puntos de Calor:",puntos)
    print ("Puntos de Calor Mexico:",puntosMexico)
    #print ("Longitud: ",x)
    #print ("Latitud: ",y)
    #print ("Tiempo inicial procesamiento: ",tiempoIni)
    #print ("Tiempo final procesamiento: ",tiempoTer)
    
    #plotPuntos(x,y)
    
    coordenadas = {'lon':x,'lat':y,'tmpIni':tiempoIni,'tmpFin':tiempoTer}
            
    return csv,puntos,coordenadas,csvArchivo,fechaPC,puntos,puntosMexico    

def PuntosCalor(path):
    
    copiaCSV()
    
    csv = archivoCSV(path)

    csv,puntos,coordenadas,csvArchivo,fechaPC,puntos,puntosMexico  = dataCSV(path+csv)
    
    borraCSV()
    
    return csv,puntos,coordenadas,csvArchivo,fechaPC,puntos,puntosMexico    
    
#path = "/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_PuntosCalor/"

#csv,puntos,coordenadas,csvArchivo,fechaPC,puntos,puntosMexico = PuntosCalor(path)

#print csv,puntos,coordenadas,csvArchivo,fechaPC,puntos,puntosMexico





