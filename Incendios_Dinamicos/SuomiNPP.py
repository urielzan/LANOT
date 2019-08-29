# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 02:04:22 2019

@author: on_de
"""
import matplotlib
matplotlib.use('Agg')
from osgeo import gdal,osr
import numpy as np
import matplotlib.pyplot as plt 
import cartopy.crs as crrs
import os

np.set_printoptions(suppress=True,formatter={'float_kind':'{:f}'.format})

def archivosSuomiNPP(path):
    print ('Listando archivos...')
    archivos = []

    for i in range(12):
        if 2 < i+1 < 6:
            tifs = os.listdir(path+'C0'+str(i+1))
            tifs.sort()
            tif_1 = tifs[0] 
            tif_2 = tifs[1]
            tif_3 = tifs[2]            
            archivos.append(path+'C0'+str(i+1)+'/'+tif_1)
            archivos.append(path+'C0'+str(i+1)+'/'+tif_2)
            archivos.append(path+'C0'+str(i+1)+'/'+tif_3)
            
        if 9 < i+1 < 13:
            tifs = os.listdir(path+'C'+str(i+1))    
            tifs.sort()
            tif_1 = tifs[0] 
            tif_2 = tifs[1]
            tif_3 = tifs[2]            
            archivos.append(path+'C'+str(i+1)+'/'+tif_1)
            archivos.append(path+'C'+str(i+1)+'/'+tif_2)
            archivos.append(path+'C'+str(i+1)+'/'+tif_3)

    return  archivos

def verificaPaso(archivos):
    print ('Verificando ultimo paso SuomiNPP...')
    paso2 = archivos[1] 
    paso1 = archivos[2]
    
    diapaso2 = int(paso2[paso2.find('2019.')+7:paso2.find('2019.')+9])
    diapaso1 = int(paso1[paso1.find('2019.')+7:paso1.find('2019.')+9])
    
    if diapaso2 > diapaso1:
        paso = 2
    else:
        paso = 1
    

    print 'Paso SuomiNPP: ',paso
    
    return paso

def SuomiNPP_1paso(archivos):
    print ('Listando archivos de 1 paso...')
    b3 = archivos[2]
    b4 = archivos[5]
    b5 = archivos[8]
    b10 = archivos[11]
    b11 = archivos[14]           
    b12 = archivos[17]
    
    #print b3,b4,b5,b10,b11,b12
    
    return b3,b4,b5,b10,b11,b12

def SuomiNPP_2pasos(archivos):
    print ('Listando archivos de 2 pasos...')
    b3_1 = archivos[1]
    b3_2 = archivos[0]
    b4_1 = archivos[4]
    b4_2 = archivos[3]
    b5_1 = archivos[7]
    b5_2 = archivos[6]
    b10_1 = archivos[10]
    b10_2 = archivos[9]
    b11_1 = archivos[13]
    b11_2 = archivos[12]
    b12_1 = archivos[16]
    b12_2 = archivos[15]
    
    #print b3_1,b3_2,b4_1,b4_2,b5_1,b5_2,b10_1,b10_2,b11_1,b11_2,b12_1,b12_2


    return b3_1,b3_2,b4_1,b4_2,b5_1,b5_2,b10_1,b10_2,b11_1,b11_2,b12_1,b12_2

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
    ymax = 33.5
    
    ds_1 = gdal.Open(paso1)
    ds_2 = gdal.Open(paso2)
    
    gdal.Warp('data_1_4326.tif',ds_1,options=gdal.WarpOptions(dstSRS='EPSG:4326',dstNodata=-9999))
    gdal.Warp('data_2_4326.tif',ds_2,options=gdal.WarpOptions(dstSRS='EPSG:4326',dstNodata=-9999))

    ds_1 = gdal.Open('data_1_4326.tif')
    ds_2 = gdal.Open('data_2_4326.tif')
    
    gdal.Translate('data_1_4326_rec.tif',ds_1,options = gdal.TranslateOptions(projWin=[xmin,ymax,-94.5,ymin]))
    gdal.Translate('data_2_4326_rec.tif',ds_2,options = gdal.TranslateOptions(projWin=[-94.5,ymax,xmax,ymin]))

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
    ymax = 33.5
    
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

def dataVentana(coorVentana):
    print ('Obteniendo datos de ventana...')   
    
    ds = gdal.Open('tmp.tif')   
    
    gdal.Translate('tmp_rec.tif',ds,options = gdal.TranslateOptions(projWin=coorVentana,noData=np.nan))
    #gdal.Translate('data_1_4326_rec.tif',ds_1,options = gdal.TranslateOptions(projWin=[-118,33,-96,12]))
    
    ds = gdal.Open('tmp_rec.tif')
    data = ds.ReadAsArray()
    
    ds = None
    
    os.remove('tmp.tif')
    os.remove('tmp_rec.tif')
    
    return data

def correcionGamma(data,gamma):
    print ('Aplicando correcion gamma...')   
    data = np.power(data, gamma)
    
    return data 

def normaliza(data):
    print ('Normalizando dato...')   
    data = (data - np.nanmin(data))*255/(np.nanmax(data)-np.nanmin(data))
    
    return data

def compuestoRGB(r,g,b):
    print ('Creando compuesto RGB...')   
    rgb = (np.dstack((r,g,b))).astype('uint8')    
    
    return rgb

def plotRGB(rgb,coorVentana,x,y,salida):
    print ('Ploteando datos RGB...')   
    
        
    salida = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/output/'+salida
    
    plt.figure(figsize=(10,10))
    ax = plt.axes(projection=crrs.PlateCarree())
    ax.coastlines(resolution='50m',color='w')
    #ax.gridlines(linestyle='--')
    ax.set_extent([coorVentana[0],coorVentana[2],coorVentana[3],coorVentana[1]])
    plt.imshow(rgb,extent=[coorVentana[0],coorVentana[2],coorVentana[3],coorVentana[1]])
    plt.plot(x,y,'r+',markersize = 20)
    
    imagen = salida+str(x)+'_'+str(y)+'.png'
    
    plt.savefig(imagen,dpi=300,bbox_inches='tight', pad_inches=0)

    rgb = None  

    return imagen

def FTSuomiNPP(archivos,paso,x,y,offset):
    print ('Generando Fire Temperature VIIRS Suomi-NPP...')   
       
    coorVentana = coordenadasVentana(x,y,offset)
    
    if paso == 2:        
        
        archivos = SuomiNPP_2pasos(archivos)
        
        b12, xmin, ymin, xmax, ymax, nx, ny = paso2SuomiNPP(archivos[10],archivos[11])
        creaTiff(b12, xmin, ymin, xmax, ymax, nx, ny)
        r = dataVentana(coorVentana)
        
        b11, xmin, ymin, xmax, ymax, nx, ny = paso2SuomiNPP(archivos[8],archivos[9])
        creaTiff(b11, xmin, ymin, xmax, ymax, nx, ny)
        g = dataVentana(coorVentana)
        
        b10, xmin, ymin, xmax, ymax, nx, ny = paso2SuomiNPP(archivos[6],archivos[7])
        creaTiff(b10, xmin, ymin, xmax, ymax, nx, ny)
        b = dataVentana(coorVentana)
        
    if paso == 1:
        
        archivos = SuomiNPP_1paso(archivos)
        
        b12, xmin, ymin, xmax, ymax, nx, ny = paso1SuomiNPP(archivos[5])
        creaTiff(b12, xmin, ymin, xmax, ymax, nx, ny)
        r = dataVentana(coorVentana)
        
        b11, xmin, ymin, xmax, ymax, nx, ny = paso1SuomiNPP(archivos[4])
        creaTiff(b11, xmin, ymin, xmax, ymax, nx, ny)
        g = dataVentana(coorVentana)
        
        b10, xmin, ymin, xmax, ymax, nx, ny = paso1SuomiNPP(archivos[3])
        creaTiff(b10, xmin, ymin, xmax, ymax, nx, ny)
        b = dataVentana(coorVentana)    
        
    r = normaliza(r)
    g = normaliza(g)
    b = normaliza(b)
           
    #r = (r-273)/(333-273)
    #g = (g-0)/(1-0)
    #b = (b-0)/(.75-0)
    
    if paso == 2:
        r = np.power(r, 1.1)
    
    elif paso == 1:
        r = np.power(r, 1.03)
    
    rgb = compuestoRGB(r,g,b)
    
    imagen = plotRGB(rgb,coorVentana,x,y,'SuomiNPP_FT_')
    
    return imagen 

def TCSuomiNPP(archivos,paso,x,y,offset):
    print ('Generando True Color VIIRS Suomi-NPP...')     
    
    coorVentana = coordenadasVentana(x,y,offset)
    
    if paso == 2:
    
        archivos = SuomiNPP_2pasos(archivos)
        
        b5, xmin, ymin, xmax, ymax, nx, ny = paso2SuomiNPP(archivos[4],archivos[5])
        creaTiff(b5, xmin, ymin, xmax, ymax, nx, ny)
        r = dataVentana(coorVentana)
        
        b4, xmin, ymin, xmax, ymax, nx, ny = paso2SuomiNPP(archivos[2],archivos[3])
        creaTiff(b4, xmin, ymin, xmax, ymax, nx, ny)
        g = dataVentana(coorVentana)
        
        b3, xmin, ymin, xmax, ymax, nx, ny = paso2SuomiNPP(archivos[0],archivos[1])
        creaTiff(b3, xmin, ymin, xmax, ymax, nx, ny)
        b = dataVentana(coorVentana)
        
        if x < -94.5 : 
            gamma = 0.01
        else :
            gamma = 0.005
    
    elif paso == 1:
                
        archivos = SuomiNPP_1paso(archivos)
        
        b5, xmin, ymin, xmax, ymax, nx, ny = paso1SuomiNPP(archivos[2])
        creaTiff(b5, xmin, ymin, xmax, ymax, nx, ny)
        r = dataVentana(coorVentana)
        
        b4, xmin, ymin, xmax, ymax, nx, ny = paso1SuomiNPP(archivos[1])
        creaTiff(b4, xmin, ymin, xmax, ymax, nx, ny)
        g = dataVentana(coorVentana)
        
        b3, xmin, ymin, xmax, ymax, nx, ny = paso1SuomiNPP(archivos[0])
        creaTiff(b3, xmin, ymin, xmax, ymax, nx, ny)
        b = dataVentana(coorVentana)
                
        
        gamma = 0.5
       
        
    r = correcionGamma(r,gamma)
    g = correcionGamma(g,gamma)
    b = correcionGamma(b,gamma)
    
    r = normaliza(r)
    g = normaliza(g)
    b = normaliza(b)
    
    rgb = compuestoRGB(r,g,b)
    
    imagen = plotRGB(rgb,coorVentana,x,y,'SuomiNPP_TC_')

    return imagen

def RGBSuomiNPPI(path,x,y,offset):
      
    archivos = archivosSuomiNPP(path)
    
    #paso = verificaPaso(archivos)
    
    paso = 2
        
    TCimagen = TCSuomiNPP(archivos,paso,x,y,offset)
    FTimagen = FTSuomiNPP(archivos,paso,x,y,offset)
    
    return TCimagen,FTimagen,paso
    
#path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_SuomiNPP/'
#x = -103
#y = 20
#offset = 1

#RGBSuomiNPPI(path,x,y,offset)
