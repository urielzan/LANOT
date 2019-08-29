    # -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 23:08:57 2019

@author: on_de
"""
import matplotlib
matplotlib.use('Agg')
import os
from osgeo import gdal,osr
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as crrs

def archivosGOES16(path):
    archivos = []
    for i in range(7):
        if i+1 != 4:     
            archivo = os.listdir(path+'C0'+str(i+1))[0]
            archivos.append(path+'C0'+str(i+1)+'/'+archivo)
    #for i in os.listdir(path):
     #   if i.endswith('.nc'):
      #      archivos.append(i)
    archivos.sort()
    return archivos

def coordenadasVentana(x,y,offset):
    print ('Obteniendo coordenadas ventana...')    

    # Obtiene las coordenadas extremas de la ventana de acuerdo al offset
    urlon= x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
    
    coorVentana = [lllon,urlat,urlon,lllat]    
    return coorVentana

    
def rebin(a, shape):
    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)

def normaliza(data):
    print ('Normalizando dato...')   
    data = (data - np.nanmin(data))*255/(np.nanmax(data)-np.nanmin(data))
    
    return data

def correcionGamma(data,gamma):
    print ('Aplicando correcion gamma...')   
    data = np.power(data, gamma)
    
    return data

def correcionContraste(color, contraste):
    F = (259*(contraste + 255))/(255.*259-contraste)
    COLOR = F*(color-.5)+.5
    COLOR = np.minimum(COLOR, 1)
    COLOR = np.maximum(COLOR, 0)    
    return COLOR

def compuestoRGB(r,g,b,entero):
    print ('Creando compuesto RGB...') 
    if entero == True:
        rgb = (np.dstack((r,g,b))).astype('uint8') 
    else:
        rgb = (np.dstack((r,g,b)))
    return rgb

def verdeSinteticoG16(C01,C02,C03):
    # Derived from Planet Labs data, CC > 0.9
    verdeSint = 0.48358168 *C02 + 0.45706946 * C01 + 0.06038137 * C03
    
    return verdeSint

def regionGOES(data,region,nvl):
    if region == 'CONUS' and nvl == 'L1b':
        # CONUS
        data = rebin(data , [3000,5000])       
       
    elif region == 'CONUS' and nvl == 'L2':
        # CONUS
        data = rebin(data , [1500,2500]) 
        
    elif region == 'FULLDISK':
        # Full Disk
        data = rebin(data , [10848,10848])   
    
    return data

def extraeNetCDFL2(path,res):
    print ('Extrayendo datos NetCDF L2"...')

    # Abre el archivo nc con em modulo NetCDF4
    nc = Dataset(path)
    
    # Extrae los valores de la variable, desenmascarando los valores, geenera un numpy.array
    data = nc.variables['CMI'][:].data
    #data = np.ma.getdata(data)
    banda = path[path.find('M3C')+3:path.find('_G16')]  
    print (banda)
    # Busca y designa el valor nulo, este valor puede variar de acuerdo al archivo
    if banda == '01':        
        data[data == 1023.] = np.nan
    elif banda == '02':
        data[data == 4095.] = np.nan
    elif banda == '03':
        data[data == 1023.] = np.nan
    elif banda == '05':
        data[data == 1023.] = np.nan
    elif banda == '06':
        data[data == 1023.] = np.nan
    elif banda == '07':
        data[data == 16383.0] = np.nan
    
    # Obtiene la constante del punto de prespectiva y las multiplica por las coordenadas extremas
    H = nc.variables['goes_imager_projection'].perspective_point_height
    xmin = nc.variables['x_image_bounds'][0] * H
    xmax = nc.variables['x_image_bounds'][1] * H
    ymin = nc.variables['y_image_bounds'][1] * H
    ymax = nc.variables['y_image_bounds'][0] * H
   
    if res == 1:
        data = rebin(data , [3000,5000])
    elif res == 2:
        data = rebin(data , [1500,2500])
        
    nx = data.shape[0]
    ny = data.shape[1]

    # Cierra el dataset
    nc.close()
    
    return data, xmin, ymin, xmax, ymax, nx, ny

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
    srs.ImportFromProj4("+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs") # Proeyeccion Goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # Exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data)   # Escribe la banda al raster
    dst_ds.FlushCache()                     # Escribe en el disco
    
    dst_ds = None
    
def dataVentana(x,y,offset):
    print('Obteniendo datos de ventana...') 
    
    coorVentana = coordenadasVentana(x,y,offset)   
    
    ds = gdal.Open('tmp.tif') 
    
    gdal.Warp('tmp_4326.tif',ds,options=gdal.WarpOptions(dstSRS='EPSG:4326',dstNodata=-9999.000))
        
    ds = gdal.Open('tmp_4326.tif')
    
    gdal.Translate('tmp_4326_rec.tif',ds,options = gdal.TranslateOptions(projWin=coorVentana,noData=np.nan))
    
    ds = gdal.Open('tmp_4326_rec.tif')
    
    data = ds.ReadAsArray()
    
    data[data == -9999.000] = np.nan
    
    ds = None 
    
    os.remove('tmp.tif')
    os.remove('tmp_4326.tif')
    os.remove('tmp_4326_rec.tif')
         
    return data

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

def FTGoes16(archivos,x,y,offset):        
    
    coorVentana = coordenadasVentana(x,y,offset)
    
    b7, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(archivos[5],2)
    creaTiff(b7, xmin, ymin, xmax, ymax, nx, ny)
    r = dataVentana(x,y,offset)

    b6, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(archivos[4],2)
    creaTiff(b6, xmin, ymin, xmax, ymax, nx, ny)
    g = dataVentana(x,y,offset)

    b5, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(archivos[3],2)
    creaTiff(b5, xmin, ymin, xmax, ymax, nx, ny)
    b = dataVentana(x,y,offset)
            
    # Apply range limits for each channel (mostly important for Red channel)
    r = np.maximum(r, 273)
    r = np.minimum(r, 333)
    g = np.maximum(g, 0)
    g = np.minimum(g, 1)
    b = np.maximum(b, 0)
    b = np.minimum(b, .75)
    
    # Normalize each channel by the appropriate range of values (again, mostly important for Red channel)
    r = (r-273)/(333-273)
    g = (g-0)/(1-0)
    b = (b-0)/(.75-0)
    
    # Apply the gamma correction to Red channel.
    #   I was told gamma=0.4, but I get the right answer with gamma=2.5 (the reciprocal of 0.4)
    r = np.power(r, 2.5)
    
    rgb = compuestoRGB(r,g,b,False)

    imagen = plotRGB(rgb,coorVentana,x,y,'GOES16_FT_')
    
    return imagen

def TCGoes16(archivos,x,y,offset):        
    
    coorVentana = coordenadasVentana(x,y,offset)
    
    b3, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(archivos[1],1)
    creaTiff(b3, xmin, ymin, xmax, ymax, nx, ny)
    r = dataVentana(x,y,offset)

    b2, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(archivos[2],1)
    creaTiff(b2, xmin, ymin, xmax, ymax, nx, ny)
    g = dataVentana(x,y,offset)

    b1, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(archivos[0],1)
    creaTiff(b1, xmin, ymin, xmax, ymax, nx, ny)
    b = dataVentana(x,y,offset)
       
    r = correcionGamma(r,0.3)
    g = correcionGamma(g,0.1)
    b = correcionGamma(b,0.3)

    r = normaliza(r)
    g = normaliza(g)
    b = normaliza(b)
    
    g = verdeSinteticoG16(b,r,g)
   
    rgb = compuestoRGB(r,g,b,True)
   
    imagen = plotRGB(rgb,coorVentana,x,y,'GOES16_TC_')
    
    return imagen

def RGBGoes16(path,x,y,offset):
    
    archivos = archivosGOES16(path)
    
    TCimagen = TCGoes16(archivos,x,y,offset)
    
    FTimagen = FTGoes16(archivos,x,y,offset)
    
    return TCimagen,FTimagen
    
#path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_GOES16/'
#x = -103
#y = 20
#offset = 1

#print (archivosGOES16(path))
#RGBGoes16(path,x,y,offset)
    
    
    
    
    
    
    
    
    
    
    
    
