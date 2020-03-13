#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 16:50:24 2020

@author: urielm
"""

import pandas as pd
from descargaAWShistorical_S3 import descargaTrack,descargaAWS
from eventoNC import creaEventoNC
from videoEventos import convert
import sys

df = pd.read_csv('./data_csv/eventosTropicales_DGRU.csv')

for anio,eveNOAA,eve,nombre,tipo_cic,region,shp,pdf,kmz in zip(df['anio'],df['eventoNOAA'],df['evento'],df['nombre'],df['tipo_cic'],df['region'],df['url_SHP'],df['url_PDF'],df['url_KMZ']):    
   
    if anio == int(sys.argv[1]):
        
        print('Año:',anio)
        print('Numero evento NOAA:',"{:02d}".format(eveNOAA))
        print('Numero evento :',"{:02d}".format(eve))
        print('Nombre:',nombre)
        print('Tipo ciclon:',tipo_cic)
        print('Region:',region)
        print('Shapefile:',shp)
        print('PDF:',pdf)
        print('KMZ:',kmz)
        
        producto = 'ABI-L2-CMIPF'
        productoNom = 'ABI-L2-CMIF-C13'
        variable = 'CMI'
        ext = 4
        numEventoNOAA = "{:02d}".format(eveNOAA)
        numEvento = "{:02d}".format(eve)
        nomEvento = nombre
        region = region
        tipoCiclon = tipo_cic  
        anio = str(anio)
        
        pathOutputSHP = './data_shp/'
        pathOutputTif = './data_tif/'
        pathOutputTrack = './data_track/'
       
        print('====================================================')
        print('INICIO DEL PROCESAMIENTO')
        print('====================================================')
    
        # EVENTO TIF
        # ==========================================================================
        descargaTrack(anio,shp,region,numEvento,nomEvento,pathOutputSHP)
        #extension = trackExtencion(anio,numEvento,nomEvento,pathOutputSHP)
        descargaAWS(anio,producto,productoNom,variable,ext,numEvento,nomEvento,region,pathOutputTif,pathOutputSHP,pathOutputTrack)   
    
        # EVENTO NC y PNG
        # ==========================================================================
        eventoDGRU = 'CiclonesTropicales_'+tipoCiclon
        #producto = 'ABI-L2-CMI-C13'
        productoMapa = 'GOES-16/ABI CMI Banda 13 (10.3 µm) Temperatura C°'
    
        pathInputMeta = './data_metadato/'
        pathOutputNC = './data_nc/'
        pathOutputPNG = './data_png/'
        pathOutputMap = './data_map/'
        
        creaEventoNC(nomEvento,region,productoNom,productoMapa,eventoDGRU,tipoCiclon,anio,numEvento,pathOutputTif,pathOutputNC,pathOutputPNG,pathOutputMap,pathOutputTrack,pathInputMeta)
    
        # EVENTO VIDEO
        # ==========================================================================
        scale='1500'
        #scale='720'
        pathOutputVideo = '/home/urielm/Documents/EVENTOS_DGRU_LANOT/eventoNC/pruebaScript/scripts/data_video/'    
        pathOutputVideoMap = '/home/urielm/Documents/EVENTOS_DGRU_LANOT/eventoNC/pruebaScript/scripts/data_videomap/'
    
        convert(pathOutputPNG,pathOutputVideo,scale,region,numEvento,nomEvento,productoNom,anio)
        convert(pathOutputMap,pathOutputVideoMap,scale,region,numEvento,nomEvento,productoNom,anio)
