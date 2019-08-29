# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 02:04:22 2019

@author: on_de
"""
#import matplotlib
#matplotlib.use('Agg')
from osgeo import gdal,osr
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.patches import Rectangle
import cartopy.crs as crrs
import os
import Sentinel2
import dataSentinel2

np.set_printoptions(suppress=True,formatter={'float_kind':'{:f}'.format})

def archivosSuomiNPP(path):
    print ('Listando archivos...')
    archivos = []
    tifs = os.listdir(path)
    tifs.sort()
    for i in tifs:
        archivos.append(path+i)
    
    return  archivos

def verificaPaso(archivos):
    print ('Verificando ultimo paso SuomiNPP...')
    paso1 = archivos[0] 
    paso2 = archivos[1]
    
    diapaso1 = int(paso1[paso1.find('2019.')+7:paso1.find('2019.')+9])
    diapaso2 = int(paso2[paso2.find('2019.')+7:paso2.find('2019.')+9])
    #print diapaso1,diapaso2
    if diapaso2 > diapaso1:
        paso = 2
    else:
        paso = 1    

    print 'Paso SuomiNPP: ',paso
    
    return paso

def SuomiNPP_1paso(archivos):
    print ('Listando archivos de 1 paso...')
    sstTiff = archivos[0]
    #print sstTiff
    return [sstTiff]

def SuomiNPP_2pasos(archivos):
    print ('Listando archivos de 2 pasos...')
    sstTiff_1 = archivos[2]
    sstTiff_2 = archivos[1]
    #print sstTiff_1,sstTiff_2
    
    return [sstTiff_1,sstTiff_2]

def coordenadasVentana(x,y,offset):
    print ('Obteniendo coordenadas ventana...')    

    # Obtiene las coordenadas extremas de la ventana de acuerdo al offset
    urlon= x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
    
    coorVentana = [lllon,urlat,urlon,lllat]    
    return coorVentana
 
def creaTiff(data, xmin, ymin, xmax, ymax, nx, ny):
    print ('Creando tif...')   
    
    # Parametros para la creacion del TIFF por medio de GDAL
    xres = (xmax - xmin) / float(ny)
    yres = (ymax - ymin) / float(nx)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    dst_ds = gdal.GetDriverByName('GTiff').Create('tmp.tif', ny, nx, 1, gdal.GDT_Float32)
    
    # Aplica la geotransformacion y la proyección
    dst_ds.SetGeoTransform(geotransform)    # Coordenadas especificas
    srs = osr.SpatialReference()            # Establece el ensamble
    srs.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ") 
    dst_ds.SetProjection(srs.ExportToWkt()) # Exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data)   # Escribe la banda al raster
    dst_ds.FlushCache()                     # Escribe en el disco
    
    dst_ds = None
    
def paso2SuomiNPP(paso1,paso2):
    print ('Obteniendo datos...\nUniendo paso 1 y paso 2...')   
    
    xmin = -118
    xmax = -85
    ymin = 12
    ymax = 35
    
    ds_1 = gdal.Open(paso1)
    ds_2 = gdal.Open(paso2)
    
    gdal.Warp('data_1_4326.tif',ds_1,options=gdal.WarpOptions(dstSRS='EPSG:4326',dstNodata=-9999))
    gdal.Warp('data_2_4326.tif',ds_2,options=gdal.WarpOptions(dstSRS='EPSG:4326',dstNodata=-9999))

    ds_1 = gdal.Open('data_1_4326.tif')
    ds_2 = gdal.Open('data_2_4326.tif')
    
    gdal.Translate('data_1_4326_rec.tif',ds_1,options = gdal.TranslateOptions(projWin=[xmin,ymax,-96.5,ymin]))
    gdal.Translate('data_2_4326_rec.tif',ds_2,options = gdal.TranslateOptions(projWin=[-96.5,ymax,xmax,ymin]))

    ds_1 = gdal.Open('data_1_4326_rec.tif')
    ds_2 = gdal.Open('data_2_4326_rec.tif')

    data_1 = ds_1.ReadAsArray()
    data_2 = ds_2.ReadAsArray()

    data = np.concatenate((data_1,data_2), axis=1)
    
    data[data == -9999.000000] = np.nan
    data[data == -340282346638528859811704183484516925440.000000] = np.nan
    
    nx = data.shape[0]
    ny = data.shape[1]
    
    ds_1 = None
    ds_2 = None
    data_1 = None
    data_2 = None
            
    os.remove('data_1_4326.tif')
    os.remove('data_2_4326.tif')
    os.remove('data_1_4326_rec.tif')
    os.remove('data_2_4326_rec.tif')
        
    return data, xmin, ymin, xmax, ymax, nx, ny

def paso1SuomiNPP(paso1):
    print ('Obentiendo datos...')   
    
    xmin = -118
    xmax = -85
    ymin = 12
    ymax = 35
    
    ds_1 = gdal.Open(paso1)

    gdal.Warp('data_1_4326.tif',ds_1,options=gdal.WarpOptions(dstSRS='EPSG:4326',dstNodata=-9999))

    ds_1 = gdal.Open('data_1_4326.tif')
    
    gdal.Translate('data_1_4326_rec.tif',ds_1,options = gdal.TranslateOptions(projWin=[xmin,ymax,xmax,ymin]))
    
    ds_1 = gdal.Open('data_1_4326_rec.tif')

    data = ds_1.ReadAsArray()
    
    data[data == -9999.000000] = np.nan
    data[data == -340282346638528859811704183484516925440.000000] = np.nan
    
    nx = data.shape[0]
    ny = data.shape[1]
    
    ds_1 = None
            
    os.remove('data_1_4326.tif')
    os.remove('data_1_4326_rec.tif')
        
    return data, xmin, ymin, xmax, ymax, nx, ny

def buscadorTif(ds,x,y):
  
    # Abre el raster 
    #ds = gdal.Open(tif)
    
    # Si no lo puede abrir termina el proceso
    if ds is None:
        print ('No se pudo abrir el raster temporal')
        return 'sin calcular'        
    else:
        print ('Buscando pixel...')
    
    # Datos de la geotransformación
    geotransform = ds.GetGeoTransform() 
    xMin = geotransform[0] # X de origen
    yMax = geotransform[3] # Y de origen
    resx = geotransform[1] # Tamaño de pixel
    resy = geotransform[5] # Tamaño de pixel
          
    data = ds.ReadAsArray() # Lee el array
    
    yMin = yMax - resx*data.shape[0]
        
    # Obtiene los índices
    xOffset = int((x - xMin) / resx)
    yOffset = int((y - yMin) / resy)

    # Obtiene el valor individual de acuerdo a los indices
    value = data[yOffset,xOffset]
        
    return value   

def dataVentana(coorVentana):
    print ('Obteniendo datos de ventana...')   
    
    ds = gdal.Open('tmp.tif')   
    
    gdal.Translate('tmp_rec.tif',ds,options = gdal.TranslateOptions(projWin=coorVentana,noData=np.nan))
    #gdal.Translate('data_1_4326_rec.tif',ds_1,options = gdal.TranslateOptions(projWin=[-118,33,-96,12]))
    
    ds = gdal.Open('tmp_rec.tif')
    data = ds.ReadAsArray()
    
    value = buscadorTif(ds,x,y)
    
    ds = None
    
    os.remove('tmp.tif')
    os.remove('tmp_rec.tif')
    
    return data,value

def calculaTicks(dataMin,dataMax):
   
    inter = 0
    # Obtiene los intervalos basado en el minimo y maximo de los valores dentro de la ventana     
    if dataMin >= 0 :
        inter = dataMax - dataMin 
        
    elif dataMin < 0 and dataMax > 0:
        inter = dataMax + abs(dataMin)
        
    elif dataMin < 0 and dataMax <= 0:
        inter = abs(dataMin) - abs(dataMax)
     
    # Define el número de valores que se mostraran en la barra de color    
    tick1 = dataMin + inter/8
    tick2 = dataMin + inter*2/8
    tick3 = dataMin + inter*3/8
    tick4 = dataMin + inter*4/8
    tick5 = dataMin + inter*5/8
    tick6 = dataMin + inter*6/8
    tick7 = dataMin + inter*7/8     
    
    return tick1,tick2,tick3,tick4,tick5,tick6,tick7


def plotRGB(rgb,varBus,coorVentana,x,y,offset,salida,varName,stdName,unidades):
    print ('Ploteando datos RGB...')   
    
    salida = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/output/'+salida

    
    plt.figure(figsize=(10,10))
    #ax = plt.axes(projection=crrs.Geodetic(globe=crrs.Globe(datum='WGS84', ellipse='WGS84')))
    ax = plt.axes(projection=crrs.PlateCarree())
    ax.coastlines(resolution='50m',color='k')
    #ax.gridlines(linestyle='--')
    ax.set_extent([coorVentana[0],coorVentana[2],coorVentana[3],coorVentana[1]])
    
    sen = plt.imread('tmp_4326Sen.tif')    
    plt.imshow(sen,extent=[coorVentana[0],coorVentana[2],coorVentana[3],coorVentana[1]])
    
    plt.imshow(rgb,extent=[coorVentana[0],coorVentana[2],coorVentana[3],coorVentana[1]],alpha=0.7,cmap='coolwarm',vmin=20)
    
    # Agrega una barra de color
    tick1,tick2,tick3,tick4,tick5,tick6,tick7 = calculaTicks(20,np.nanmax(rgb))   
    
    cb = plt.colorbar( ticks=[tick1,tick2,tick3,tick4,tick5,tick6,tick7], orientation = 'horizontal', pad = 0, shrink = 0.83)
    cb.ax.set_xticklabels([str(round(tick1,2)),str(round(tick2,2)),str(round(tick3,2)),str(round(tick4,2)),str(round(tick5,2)),str(round(tick6,2)),str(round(tick7,2))])
    cb.outline.set_visible(True) # Coloca una línea en el borde
    cb.ax.tick_params(width = 0) # Remueve los ticks
    cb.ax.xaxis.set_tick_params(pad=-20) # Pone lo valores de los intervalos dentro de la barra
    cb.ax.tick_params(axis='x', colors='black', labelsize=10) # Define el color y tamaño de la letra de los ticks
    
    plt.plot(x,y,'k+',markersize = 20)
    
    currentAxis = plt.gca()
    currentAxis.add_patch(Rectangle((x-offset,  y-offset/1.0),offset*0.75 ,offset*0.18 , alpha=1, facecolor='silver', zorder = 3,ec="black", lw=1.0))
	     
	# Agrega los datos de la variable al rectángulo 
    plt.text(x-offset/1.02, y-offset/1.25,'Variable: '+varName+'\nNombre Estandar: '+stdName+'\nUnidades: '+unidades, fontsize=8,color = 'white')

	# Agrega los datos de la ventana
    plt.text(x-offset/1.02, y-offset/1.035, 'Maximo: '+str(round(np.nanmax(rgb),2))+'\nMinimo:  '+str(round(np.nanmin(rgb),2))+'\nMedia:    '+str(round(np.nanmean(rgb),2)),fontsize=8)
	    
	# Agrega los datos de la coordenada
    #plt.text(x-offset/1.38, y-offset/1.07,'\nLatitud:    '+str(abs(round(y,2)))+'\nLongitud: '+str(abs(round(x,2))), fontsize=15)
	    
	# Agrega el valor y la calidad del dato de acuerdo al subdataset DQF, que define la calidad con la que fueron calculados los datos, este se encuentra
	# en todos los NetCDF L1b y L2 de Goes, lo define por el color de la letra

    if varBus == np.nan:
        calColor = 'b'
        calidad = 'Algoritmo no procesado'
    else:    
        calColor = 'g'
        calidad = 'Algoritmo procesado'

    plt.text(x-offset/1.6,  y-offset/1.09,str(round(float(varBus),2)), fontsize=24, color=calColor)
    plt.text(x-offset/1.45,  y-offset/1.05,calidad,fontsize=7, color=calColor)
           
    imagen = salida+str(x)+'_'+str(y)+'.png'
    
    plt.savefig(imagen,dpi=300,bbox_inches='tight', pad_inches=0)
    
    sen = None
    rgb = None  
    
    return imagen


def SSTSuomiNPP(archivos,paso,x,y,offset):
    print ('Generando True Color VIIRS Suomi-NPP...')     
    
    coorVentana = coordenadasVentana(x,y,offset)

    if paso == 2:
    
        archivos = SuomiNPP_2pasos(archivos)        
        
        sst, xmin, ymin, xmax, ymax, nx, ny = paso2SuomiNPP(archivos[0],archivos[1])
        
        creaTiff(sst, xmin, ymin, xmax, ymax, nx, ny)
        sst,sstValue = dataVentana(coorVentana)
        sst[sst <= 20] = np.nan
        
        print 'SST:',sstValue
                
         
    elif paso == 1:
                
        archivos = SuomiNPP_1paso(archivos)
        
        sst, xmin, ymin, xmax, ymax, nx, ny = paso1SuomiNPP(archivos[0])
        creaTiff(sst, xmin, ymin, xmax, ymax, nx, ny)
        sst,sstValue = dataVentana(coorVentana)
               
    # gb,varBus,coorVentana,x,y,offset,salida,varName,stdName,unidades 
    imagen = plotRGB(sst,sstValue,coorVentana,x,y,offset,'SuomiNPP_SST_','SST','Sea Surface Temperature','C')

    return imagen,sstValue

def RGBSuomiNPPI(path,x,y,offset):
    
    dataSentinel2.extraeWMS(x,y,offset,'1-NATURAL-COLOR,DATE','TC_',pathSen,'TC')
    archivo = Sentinel2.RGBSentilen2(x,y,offset,'TC',pathSen)
    
    archivos = archivosSuomiNPP(path)
    
    print archivos 
    paso = verificaPaso(archivos)
    print paso
    #paso = 1
    #SuomiNPP_1paso(archivos)
    #SuomiNPP_2pasos(archivos)
        
    SSTimagen,SSTvalue = SSTSuomiNPP(archivos,paso,x,y,offset)
    
    Sentinel2.borraTmp()
    dataSentinel2.borraTodo(archivo)
    
    
    return SSTimagen,SSTvalue,paso
    
path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_SuomiNPP/SST/'
pathSen = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/data_Sentinel2/'
x = -87
y = 22
offset = 0.3

print RGBSuomiNPPI(path,x,y,offset)
