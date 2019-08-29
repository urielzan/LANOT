# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 21:22:04 2018

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
import EMAS_GOES16
import ensambleCoor
import dataGOES16
#from plotBuscadorGoes16 import plotBuscador
#import winsound
#from xlrd import XLRDError
#from sentinelDyn import sentinelPNG


#for i in estActivas:

def url_xls(url):
    
    # Descarga los datos de las estaciones EMAS deacuerdo a si id, servidor del SMN    
    http = urllib3.PoolManager()
    r = http.request('GET', url, preload_content=False)
    
    # Nombre del archivo a partir del URL
    filename = url[url.rfind("/exc/")+5:-4]
    
    print ("Descargando %s..." % filename)
    
    # Escribe Archivo temporal local XLS   
    f = open(filename+'.xls', "wb")
    
    # Escribe en un nuevo fichero local los datos obtenidos vía HTTP.
    f.write(r.read())
    
    # Cierra ambos
    f.close()
    r.close()
    
    return filename
    
def xsl_dataframe(filename):
    
    # Convierte los archivos de xlsx a csv con pandas
    data_xls = pd.read_excel(filename + ".xls", index_col=None)
    data_xls.to_csv(filename+'.csv', encoding='utf-8', index=False)
    df=pd.read_csv(filename+'.csv', sep=',',header=None)
    
    # Borra el archivo xlsx
    os.remove(filename + ".xls")
        
    # Convierte el csv a un dataframe de pandas
    df=pd.read_csv(filename+'.csv', sep=',',header=None)
    
    # Borra el archivo csv
    os.remove(filename+'.csv')
    
    # Describe caracteristicas del Dataframe
    #print (df.shape)
    #print (df.describe())
    #print (df[0].head())
    
    return df

def datosEstacion(df):
    
    # Asigna valores de la estacion
    estacion = df.iat[0,1]
    ubicacion = df.iat[0,2]
    operador = df.iat[1,1]
    altitud = df.iat[2,5]
    
    lon = df.iloc[2,1]
    lonDeg = float(lon[:lon.find('\xc2\xb0')])
    lonMin = float(lon[lon.find('\xc2\xb0')+2:lon.find('\xc2\xb0')+4])
    lonSeg = float(lon[lon.find('\xc2\xb0')+5:lon.find('\xc2\xb0')+7])
    lon = lonDeg + lonMin/60 + lonSeg/3600

    lat = df.iloc[2,3]
    latDeg = float(lat[:lat.find('\xc2\xb0')])
    latMin = float(lat[lat.find('\xc2\xb0')+2:lat.find('\xc2\xb0')+4])
    latSeg = float(lat[lat.find('\xc2\xb0')+5:lat.find('\xc2\xb0')+7])
    lat = latDeg + latMin/60 + latSeg/3600
    
    return estacion,ubicacion,operador,altitud,-lon,lat

def extraeVariables(df):
    
    # Asigna variables a numpy arrays
    temperatura = df.iloc[5:,5].values
   
    # Convierte los valores a flotantes
    temperatura = temperatura.astype(float) 
       
    # Invierte los valores
    #temperatura = np.fliplr([temperatura])[0]
        
    return temperatura

def extraeTiempo(df):
    
    # Separa las fehas de la horas
    df[['fecha', 'hora']] = df[0].str.split(' ', n=1, expand=True)
    df[['horas','minutos']] = df['hora'].str.split(':', n=1, expand=True)
    df[['min','segundos']] = df['minutos'].str.split(':', n=1, expand=True)
   
    # Asigna las variables de horas, fechas y hora  
    fecha = df.iloc[5:,10].values
    hora = df.iloc[5:,11].values
    horas = df.iloc[5:,12].values
    minutos = df.iloc[5:,14].values      
        
    # Invierte las horas    
    #fecha = np.fliplr([fecha])[0] 
    #hora = np.fliplr([hora])[0]
    #horas = np.fliplr([horas])[0]
    #minutos = np.fliplr([minutos])[0]
    
    return fecha,hora,horas,minutos

def creaGrafica(tickx,ticky,tiempo,tiempoG16,variable,satVariable,nomVariable,unidad,simbolo,estacion,ubicacion):
    
    # Tamaña de la grafica
    fig = plt.figure(figsize=(6,4))
    #fig.patch.set_facecolor('#2E2E2E')
    
    # Espaciamento de los labels
    tick_spacing = tickx
    tick_spacing_y = ticky
    
    # Asigan los datos a la grafica
    ax = plt.axes()
    ax.set_facecolor('#939393')    
    ax.plot(tiempo,variable,simbolo,markersize=1,label='Temperatura EMAS')
    ax.plot(tiempoG16,satVariable,'b+',markersize=5,label='LST Goes-16 / ABI')
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


def descargaEMAS(estacion):
    
    # URL de descarag del servido del SMN, para las estaciones EMAS en 24 horas, formato xls
    url = "http://smn1.conagua.gob.mx/emas/exc/"+estacion+"_10M.xls"
    
    # Crea el archivo xls a aprtir de la URL
    filename = url_xls(url)
    print filename
    # Convierte el xls a csv y despues a un dataframe de pandas
    df = xsl_dataframe(filename)    
    
    # Remplasar nan por 0
    df = df.replace(np.nan, 0)    
        
    # Asigna valores de la estacion
    estacion,ubicacion,operador,altitud,lon,lat = datosEstacion(df)

    # Extrae variables
    temperatura = extraeVariables(df)
    
    # Extrae tiempos    
    fecha,hora,horas,minutos = extraeTiempo(df)
    
    # Crea Graficas
    #creaGrafica(10,1,horas+minutos,temperatura,'Temperatura','(C)','r',estacion,ubicacion)
           
    # Impresion de datos de la estacion
    print 'Estacion:',estacion
    print 'Ubicacion:',ubicacion
    print 'Oprador:',operador
    print 'Altitud:',altitud
    print 'Latitud:',lat
    print 'Longitud:',lon
    
    return estacion,ubicacion,operador,altitud,lon,lat,temperatura,fecha,hora,horas,minutos
    #return estacion,ubicacion,y,x

def EMAS_LST(estaciones,pathLST,pathSen,pathEMAS,pathEMAS_LST,pathSalida,offset):
    #os.remove('/var/www/html/EMAS_LST/*')
    dataGOES16.extraeNetCDF()
    for i in estaciones:    
        try:
            estacion,ubicacion,operador,altitud,lon,lat,temperatura,fecha,hora,horas,minutos = descargaEMAS(i)
            LSTimagen,lstValue,fechaG16,tiempoG16 = EMAS_GOES16.RGBGoes16(pathLST,pathSen,lon,lat,offset)
            
            tiempoUG16 = tiempoG16
            lstUValue = lstValue
            
            data_lst_EMAS = open(pathEMAS+i+'.csv','a')
            data_lst_EMAS.write('\n'+str(lstValue)+','+str(tiempoG16))
            data_lst_EMAS.close()
            
            csv_lst_emas = pd.read_csv(pathEMAS+i+'.csv')
                    
            lstValue24 = csv_lst_emas.iloc[0:,0].values.tolist()
            #tiempoG1624 = csv_lst_emas.iloc[0:,1].values.tolist()
            #datos24 = [lstValue24,thttp://smn1.conagua.gob.mx/emas/exc/DG02_24H.xlsiempoG1624]
            #print lstValue24
            #csv_lst_emas = None
                   
            if len(lstValue24) >= 24:         
                csv_lst_emas = csv_lst_emas.iloc[1:]                        
                csv_lst_emas.to_csv(pathEMAS+i+'.csv',index=False)
             
            csv_lst_emas = pd.read_csv(pathEMAS+i+'.csv')
            lstValue = csv_lst_emas.iloc[0:,0].values
            tiempoG16 = csv_lst_emas.iloc[0:,1].values
            
            csv_lst_emas = None
            
            tiempo = []   
            for j in horas+minutos:
                tiempo.append(float(j))
            
            cont = 0   
            for j in tiempo:
                #print j
                if float(tiempoUG16)-10 <= j <= float(tiempoUG16)+10:                
                    break
                cont = cont + 1               
            #print temperatura[cont]
    
            data_lst_EMAS = open(pathEMAS_LST+i+'.csv','a')
            data_lst_EMAS.write('\n'+i+','+str(lstUValue)+','+str(temperatura[cont])+','+str(tiempoUG16)+','+str(tiempo[cont])+','+str(lon)+','+str(lat))
            data_lst_EMAS.close()
            
            data_lst_EMAS_EMC = open(pathEMAS_LST+'EMAS_lst.csv','a')
            data_lst_EMAS_EMC.write('\n'+i+','+str(lstUValue)+','+str(temperatura[cont])+','+str(tiempoUG16)+','+str(tiempo[cont])+','+str(lon)+','+str(lat)+','+str(altitud))
            data_lst_EMAS_EMC.close()
            
            creaGrafica(200,2,tiempo,tiempoG16,temperatura,lstValue,'Temperatura','(C)','r.',estacion,ubicacion)
            
            ensambleCoor.ensambleSat(lon,lat,LSTimagen,'grafica.png','ubicacion_muni.png','ubicacion_edo.png',
                                     'LANOT.png',pathSalida,estacion,ubicacion,operador,altitud)        

        except:
            print 'Estacion sin transmicion de datos'
        #return LSTimagen
        #print horas+minutos
        #SONIDO DE ALERTA
        #if np.isnan(varBus) == False:
            #winsound.PlaySound("SD_ALERT_28.wav",winsound.SND_ASYNC)
        #except: #XLRDError,ValueError:
          #  print 'Estacion sin transmicion de datos'
         #   continue
    dataGOES16.borraNetCDF()
        
estaciones = ('QR04','YC03','CM04','TB07','CS05','OX03','VR07','PU03','GR08','MO01','TL01','DF05','HI03',
              'MX04','MC02','QO01','GT01','JA05','AG01','ZC01','NY03','SL02','SI04','DG05','TM04','NL01',
              'CL16','CH22','SO08','BC06','BS16')

#try:
dataGOES16.borraNetCDF
os.system('rm /home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Estaciones_LST/data_Sentinel2/TC/*')

pathLST = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Estaciones_LST/data_GOES16/LST/'
pathSen = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Estaciones_LST/data_Sentinel2/'
pathEMAS = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Estaciones_LST/data_EMAS_LST/'
pathEMAS_LST = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Estaciones_LST/data_EMAS_LST_EMC/'
pathSalida = '/var/www/html/emas_lst/'
offset = 0.3

EMAS_LST(estaciones,pathLST,pathSen,pathEMAS,pathEMAS_LST,pathSalida,offset)
