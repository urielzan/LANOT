#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 16:29:08 2020

@author: urielm
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.nhc.noaa.gov'

anios = ['2017','2018','2019']
regiones = ['atl','epac']
        
nombres = []
eventos = []
eventosNOAA = []
tipoCiclon = []
archivosPDF = []
archivosKMZ = []
archivosSHP = []
aniosd = []
regionesE = []

        
for anio in anios: 
    evento = 1
    for region in regiones:
        urlm = url + "/data/tcr/index.php?season="+anio+"&basin="+region
        req = requests.get(urlm)
        soup = BeautifulSoup(req.content, 'html.parser')
        #print(soup.find_all("li",class_="hdr")) 
        
        resultado = soup.find_all("li",class_="hdr")
                
        for tag in resultado:
            
            if tag.contents[0].split(' ')[0] == 'Tropical' and tag.contents[0].split(' ')[1] == 'Storm':
        
                nombre = tag.contents[0].split(' ')[2]    
                ciclon = 'Tormenta Tropical'                               
                pdf = tag.contents[1].get('href')
                if pdf != None:
                    pdf = url + pdf
                    kmz = url + tag.contents[3].get('href')
                    shp = url + tag.contents[5].get('href')
                else:
                    pdf = tag.contents[3].get('href')
                    pdf = url + pdf
                    kmz = url + tag.contents[5].get('href')
                    shp = url + tag.contents[7].get('href')
                eventoNOAA =  shp.split('/')[-1].split('_')[0][2:4]
                if region == 'atl':
                    reginE = 'Atlántico'
                else:
                    reginE = 'Pacífico'
                
                nombres.append(nombre)
                eventosNOAA.append(eventoNOAA)
                eventos.append(evento)
                tipoCiclon.append(ciclon)
                archivosPDF.append(pdf)
                archivosKMZ.append(kmz)
                archivosSHP.append(shp)
                aniosd.append(anio)
                regionesE.append(reginE)
                        
                evento += 1
                #print (nombre,ciclon,pdf,kmz,shp,evento)
        
            elif tag.contents[0].split(' ')[0] == 'Tropical' and tag.contents[0].split(' ')[1] == 'Depression':
        
                nombre = tag.contents[0].split(' ')[2]
                ciclon = 'Depresión Tropical'
                pdf = tag.contents[1].get('href')
                if pdf != None:
                    pdf = url + pdf
                    kmz = url + tag.contents[3].get('href')
                    shp = url + tag.contents[5].get('href')
                else:
                    pdf = tag.contents[3].get('href')
                    pdf = url + pdf
                    kmz = url + tag.contents[5].get('href')
                    shp = url + tag.contents[7].get('href')
                if region == 'atl':
                    reginE = 'Atlántico'
                else:
                    reginE = 'Pacífico'
                
                nombres.append(nombre)
                eventosNOAA.append(eventoNOAA)
                eventos.append(evento)
                tipoCiclon.append(ciclon)
                archivosPDF.append(pdf)
                archivosKMZ.append(kmz)
                archivosSHP.append(shp)
                aniosd.append(anio)
                regionesE.append(reginE)
                
                evento += 1
                #print (nombre,ciclon,pdf,kmz,shp,evento)
                
            elif tag.contents[0].split(' ')[0] == 'Hurricane':
        
                nombre = tag.contents[0].split(' ')[1]
                ciclon = 'Huracán'
                pdf = tag.contents[1].get('href')
                if pdf != None:
                    pdf = url + pdf
                    kmz = url + tag.contents[3].get('href')
                    shp = url + tag.contents[5].get('href')
                else:
                    pdf = tag.contents[3].get('href')
                    pdf = url + pdf
                    kmz = url + tag.contents[5].get('href')
                    shp = url + tag.contents[7].get('href')
                if region == 'atl':
                    reginE = 'Atlántico'
                else:
                    reginE = 'Pacífico'
                    
                nombres.append(nombre)
                eventosNOAA.append(eventoNOAA)
                eventos.append(evento)
                tipoCiclon.append(ciclon)
                archivosPDF.append(pdf)
                archivosKMZ.append(kmz)
                archivosSHP.append(shp)
                aniosd.append(anio)
                regionesE.append(reginE)
                
                evento += 1
                #print (nombre,ciclon,pdf,kmz,shp,evento)
            
                

dic = {'nombre': nombres, 'eventoNOAA': eventosNOAA, 'evento': eventos,'anio':aniosd,
       'tipo_cic':tipoCiclon,'region':regionesE,'url_PDF':archivosPDF,
       'url_KMZ':archivosKMZ,'url_SHP':archivosSHP}

df = pd.DataFrame.from_dict(dic)

df.to_csv('./data_csv/eventosTropicales_DGRU.csv')
