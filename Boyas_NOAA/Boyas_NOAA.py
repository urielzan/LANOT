# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 00:10:58 2018

@author: urielzan
"""
import matplotlib
matplotlib.use('Agg')
import urllib3 
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from bs4 import BeautifulSoup
import requests
import ensambleCoor
import NOAA_SuomiNPP
import dataSuomiNPP
#from PlotBuscadorGoes16 import plotBuscador
#import winsound
    
def metaNOAA(url):
    
    # Realiza la peticion de descarga de la pagina web
    r  = requests.get("https://" +url)    
    data = r.text
    status_code = r.status_code
    
    if status_code != 200:
        print ('Error de descarga...')
        return

    # Scraping de la pagina HTML a travez de etiquetas con BeautifulSoup 
    soup = BeautifulSoup(data)
    
    # Listas del los metadatos de las boyas
    metadataText = []
    metadataDatos = []
    
    # Acceso a la parte de metadatos generales
    for metadata in soup.find_all('b'):        
        metadataText.append(metadata.text) 
        #print(metadata.text)
    
    # Acceso a la parte de metadatos de la boya
    for metadata in soup.find_all('h1'):        
        boyaDatos = metadata.text
        
    for metadata in soup.find_all('td'):         
        metadataDatos.append(metadata.text)
    
    # Estracion de datos de la boya con los arrays de strings
    boyaNum = str(boyaDatos[boyaDatos.find("Station")+8:boyaDatos.find("Station")+13])
    #print "\nEstacion: "+boyaNum
    ubicacion = str(boyaDatos[boyaDatos.find("-")+2:])
    #print "Ubicacion: "+ubicacion
    lat = float(metadataText[3][:6])
    #print "Latitud: ",lat
    lon = float("-"+metadataText[3][9:15])
    #print "Longitud: ",lon
    prof = str(metadataDatos[15][288:291])
    #print "Profundidad: ",prof    
    
    return boyaNum,ubicacion,lat,lon,prof

def datosBoya(url):
    
    # Peticion de descarga de la url del archivo txt        
    http = urllib3.PoolManager()
    r = http.request('GET', url, preload_content=False)
    
    # Archivo web HTML
    #r = urlopen(url)
    
    # Nombre del archivo a partir del URL
    filename = url[url.rfind("y2")+3:]
    print ("Descargando %s..." % filename)
    
    # Crea archivo local teporal
    f = open(filename, "wb")
    
    # Escribir en un nuevo fichero local los datos obtenidos vía HTTP.
    f.write(r.read())
    
    # Cerrar ambos
    f.close()
    r.close()
    
    # Convierte en un dataframe con pandas    
    df = pd.read_csv(filename, header=None, delimiter=r"\s+")
    
    #Borra el archivo txt
    os.remove(filename)
    
    #Imprime caracteristicas del dataframe
    #print (df)
    #print (df.shape)
    #print (df.describe())
    
    # Extrae datos del dataframe
    WTMP = df.iloc[2:80,14].values
               
    ano = df.iloc[2:80,0].values
    mes = df.iloc[2:80,1].values
    dia = df.iloc[2:80,2].values
    hora = df.iloc[2:80,3].values
    minuto = df.iloc[2:80,4].values
    
    #print ano,mes,dia,hora,minuto
    #Concatenacion de fecha y hora
    fecha = ano+"-"+mes+"-"+dia
    tiempo = hora+minuto
    tiempo = tiempo.astype(float)
    
    return WTMP,fecha,tiempo
    
def depurador(WTMP,time):
    
    #Asignacion de no data
    WTMP[WTMP=='MM'] = np.nan
    
    #Cambio de tipo de dato
    WTMP = WTMP.astype(float) 
    #print (WTMP)
    
    #Invierte los valores
    WTMP = np.fliplr([WTMP])[0]
    time = np.fliplr([time])[0]
    
    return WTMP,time

def creaGrafica(tickx,ticky,tiempo,tiempoSNPP,variable,SSTvalue,nomVariable,unidad,simbolo):
    
    # Tamaña de la grafica
    fig = plt.figure(figsize=(6,4))
    
    # Espaciamento de los labels
    tick_spacing = tickx
    tick_spacing_y = ticky
    
    # Asigan los datos a la grafica
    ax = plt.axes()
    ax.set_facecolor('#939393')
    ax.plot(tiempo,variable,simbolo,markersize=1,label='WTMP Boya NOAA')
    ax.plot(tiempoSNPP,SSTvalue,'b+',markersize=5,label='SST SuomiNPP / VIIRS')
    ax.legend(loc='lower left',facecolor='white',fontsize=7)
    
    # Crea la grafica
    plt.title(nomVariable,color='k')
    plt.ylabel(nomVariable+' '+unidad,color='k')
    plt.xlabel('Tiempo (Hrs)',fontsize = 11,color='k')
    ax.yaxis.set_tick_params(labelsize=6,color='k',labelcolor='k')
    ax.xaxis.set_tick_params(labelsize=6,color='k',labelcolor='k')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing_y)) 
    plt.grid(True)
    #fig.savefig('grafica.png',dpi=300,bbox_inches='tight', pad_inches=0.2,facecolor="#2E2E2E")
    fig.savefig('grafica.png',dpi=300,bbox_inches='tight', pad_inches=0.2,facecolor="white")
    fig.show()
    
def descargaBoyaNOAA(boya):
    
    # URL de los metadatos de la boya 
    url1 = "www.ndbc.noaa.gov/station_page.php?station="+boya
    
    # Obtiene la informacion de la boya atravez de scrapting
    boyaNum,ubicacion,lat,lon,prof = metaNOAA(url1)
    
    # URL de los datos de la boya de los ultimos 5 dias
    url2 = "https://www.ndbc.noaa.gov/data/5day2/"+boya+"_5day.txt"
    
    # Obtiene las variables de la boya a partir de scrapting
    WTMP,fecha,tiempo = datosBoya(url2)
    
    #print WTMP,fecha,time    
    # Depura los datos de la boya
    WTMP,tiempo = depurador(WTMP,tiempo) 
    
    # Grafica de datos ultimos 5 dias
    #creaGrafica(100,0.1,timeDep,WTMPdep,'Temperatura Superficial del Mar','C','r.',boyaNum,ubicacion)
    
    return boyaNum,ubicacion,lat,lon,prof,WTMP,fecha,tiempo

def Boya_SST(estaciones,pathSST,pathSen,pathEMAS,pathSalida,offset):
    #os.remove('/var/www/html/EMAS_LST/*')
    dataSuomiNPP.extraeGTiff()
    for i in estaciones:    
        boyaNum,ubicacion,lat,lon,prof,WTMP,fecha,tiempo = descargaBoyaNOAA(i)
        SSTimagen,SSTvalue,paso = NOAA_SuomiNPP.RGBSuomiNPP(pathSST,pathSen,lon,lat,offset)
        
        fechaSNPP,tiempoSNPP = dataSuomiNPP.revisaGTif(paso)
        #data_sst_BNOAA = open(pathEMAS+i+'.csv','a')
        #data_sst_BNOAA.write('\n'+str(SSTvalue)+','+str(tiemppSNPP))
        #data_sst_BNOAA.close()
        
        #csv_lst_emas = pd.read_csv(pathEMAS+i+'.csv')
                
        #lstValue24 = csv_lst_emas.iloc[0:,0].values.tolist()
        #tiempoG1624 = csv_lst_emas.iloc[0:,1].values.tolist()
        #datos24 = [lstValue24,tiempoG1624]
        #print lstValue24
        #csv_lst_emas = None
               
        #if len(lstValue24) >= 24:         
         #   csv_lst_emas = csv_lst_emas.iloc[1:]                        
          #  csv_lst_emas.to_csv(pathEMAS+i+'.csv',index=False)
         
        #csv_lst_emas = pd.read_csv(pathEMAS+i+'.csv')
        #lstValue = csv_lst_emas.iloc[0:,0].values
        #tiempoG16 = csv_lst_emas.iloc[0:,1].values
        
        #csv_lst_emas = None
        
        #tiempo = []   
        #for i in horas+minutos:
           # tiempo.append(float(i))
        
        creaGrafica(200,0.1,tiempo,tiempoSNPP,WTMP,SSTvalue,'Temperatura Superficial del Mar','C','r.')
        
        ensambleCoor.ensambleSat(lon,lat,SSTimagen,'grafica.png','ubicacion_muni.png','ubicacion_edo.png',
                                 'LANOT.png',pathSalida,boyaNum,ubicacion,prof)        

        #return LSTimagen
        #print horas+minutos
        #SONIDO DE ALERTA
        #if np.isnan(varBus) == False:
            #winsound.PlaySound("SD_ALERT_28.wav",winsound.SND_ASYNC)
        #except: #XLRDError,ValueError:
          #  print 'Estacion sin transmicion de datos'
         #   continue
    dataSuomiNPP.borraGTif()
    
#boyas = ['42002','42055','42020','PTAT2','42019','42035','SRST2','42001','BURL1','42040','42012','DPIA1','42039','42003','46086','46047']
#boyas = ['42002','42055','42020','PTAT2','42019','42035','42003','46086','46047']

boyas = ['42055','42020','42019','42035','42003']
#boyas = ['42055']

pathSST = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_SuomiNPP/SST/'
pathSen = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_Sentinel2/'
pathEMAS = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_BNOAA/'
pathSalida = '/var/www/html/boyas_sst/'
offset = 0.3

Boya_SST(boyas,pathSST,pathSen,pathEMAS,pathSalida,offset)


#boyaNum,ubicacion,y,x,prof = descargaBoyaNOAA(i)

#path = 'OR_ABI-L2-SSTF-M3_G16_s20180661300403_e20180661356170_c20180661400158.nc'
#var = 'SST'
#offset = 2

#varBus = plotBuscador(path,var,x,y,offset)
#print 'Boya:',boyaNum
#print 'Ubicacion:',ubicacion
#print 'Latitud:',y
#print 'Longitud:',x
#print 'Profundidad:',x

#SONIDO DE ALERTA
#if np.isnan(varBus) == False:
 #   winsound.PlaySound("SD_ALERT_28.wav",winsound.SND_ASYNC)
  

    
#print ("Sin trasnmision de datos...")     






    
