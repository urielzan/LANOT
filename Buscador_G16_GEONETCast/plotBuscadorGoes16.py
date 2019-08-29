# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 15:29:17 2018

@author: LANOT02
"""
# Librerias requeridas
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.basemap import Basemap
# Linear interpolation for color maps
from matplotlib.colors import LinearSegmentedColormap
from netCDF4 import Dataset
# En python 3 usar la versión de GDAL 2.3.1 o superior 
# En python 2.7 la versión de GDAL 2.2.4 no causa muchos problemas
from osgeo import gdal, osr
import os

import numpy as np
import time as t
# Importa la función cpt_convert
from cpt_convert import loadCPT 

def extraeNetCDF(path,var):
    """
    ==========================================================================================
    Función que obtiene los datos del NetCDF, se puede ajustar para aplicarles operaciones
    directas, ejemplo: data = data - 273.15 , en caso de querer la temperatura en Celsius,
    la operación depende de la variable
    ==========================================================================================
    """
    print ('Extrayendo datos...')

    # Abre el archivo nc con em modulo NetCDF4
    nc = Dataset(path)
    
    # Extrae los valores de la variable, desenmascarando los valores, geenera un numpy.array
    data = nc.variables[var][:]
    data = np.ma.getdata(data)
    dataCal = nc.variables['DQF'][:]    
    
    # En caso de ingresar el DQF como variable
    if var != 'DQF':
        # Busca y designa el valor nulo, este valor puede variar de acuerdo al archivo
        data[data == 65535] = np.nan
        
        # Obtiene los factores
        #scale = nc.variables[var].scale_factor
        #offset = nc.variables[var].add_offset
        
        # Aplica la escala y el offset
        #data = data * scale + offset
        
        # En caso de temperatura en Celsius
        #data = data - 273.15
    
    # Convierte los datos en tipo flotante
    #data = data.astype('float32')
    
    # Obtiene la constante del punto de prespectiva y las multiplica por las coordenadas extremas
    H = nc.variables['goes_imager_projection'].perspective_point_height
    x1 = nc.variables['x_image_bounds'][0] * H
    x2 = nc.variables['x_image_bounds'][1] * H
    y1 = nc.variables['y_image_bounds'][1] * H
    y2 = nc.variables['y_image_bounds'][0] * H

    # Obtiene datos de la variable, son requeridos para poner la información en el mapa
    varName = nc.variables[var].long_name
    stdName = nc.variables[var].standard_name
    unidades = nc.variables[var].units

    # Cierra el dataset
    nc.close()
    
    return data,dataCal,x1,x2,y1,y2,varName,stdName,unidades

def coordenadasVentana (x,y,offset):
    """
    ==========================================================================================
    Función que obtiene las coordenadas extremas, tanto del TIFF temporal para la extracción 
    de datos como el requerido para el mapeo
    ==========================================================================================
    """    
    print ('Obteniendo coordenadas ventana...')    

    # Obtiene las coordenadas extremas de la ventana de acuerdo al offset
    urlon= x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
        
    return lllon,lllat,urlon,urlat

def creaTiff(data, xmin, ymin, xmax, ymax, nx, ny):
    """
    ==========================================================================================
    Función que crea un TIFF temporal para la manipulación más sencilla de los datos, este 
    TIFF contiene todos los datos de la variable en su proyección original
    ==========================================================================================
    """    
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
   
def reproyectaTiff(x,y,offset):
    """
    ==========================================================================================
    Función que reproyecta el TIFF, primero a un sistema geográfico y después lo recorta con
    las coordenadas extremas calculadas con la función coordenadasVentana, esto lo hace por 
    medio de comandos del sistema, si se tiene instalado GDAL en el sistema se puede usar 
    el módulo subprocess, si causa problemas probar con el modulo os para llamarlo desde python
    ==========================================================================================
    """      
    print ('Reproyectando tif...')
    
    # Reproyecta el TIFF con sistema de coordenadas geoestacionario a geografico
    os.system('gdalwarp -t_srs EPSG:4326 tmp.tif tmp_4326.tif')
    #subprocess.call('gdalwarp -dstnodata -9999.0 -t_srs EPSG:4326 -of Gtiff tmp.tif tmp_4326.tif')
    
    # Obtiene las coordenadas extremas de la ventana
    coorven = []    
    coorven = coordenadasVentana(x,y,offset)

    # Recorta el TIFF en geograficas con las coordenadas de la ventana
    os.system('gdalwarp -te '+str(coorven[0])+' '+str(coorven[1])+' '+str(coorven[2])+' '+str(coorven[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_rec.tif') 
    #subprocess.call('gdalwarp -dstnodata -9999.0 -te '+str(coorven[0])+' '+str(coorven[1])+' '+str(coorven[2])+' '+str(coorven[3])+' -te_srs EPSG:4326 tmp_4326.tif tmp_4326_rec.tif')

def buscadorTif(tif,x,y):
    """
    ==========================================================================================
    Función que encuentra la fila y columna de la coordenada buscada, contando el número de 
    pixeles por unidad de la diferencia de las coordenadas extremas a la buscada
    ==========================================================================================
    """
    # Cordenadas buscadas
    points = [(x,y)]
    
    # Abre el raster 
    ds = gdal.Open(tif)
    
    # Si no lo puede abrir termina el proceso
    if ds is None:
        print ('No se pudo abrir el raster temporal')
        return 'sin calcular'        
    else:
        print ('Buscando pixel...')
    
    # Datos de la geotransformación
    transform = ds.GetGeoTransform() 
    xOrigin = transform[0] # X de origen
    #print transform[0]
    yOrigin = transform[3] # Y de origen
    #print transform[3]
    pixelWidth = transform[1] # Tamaño de pixel
    #print transform[1]
    pixelHeight = transform[5] # Tamaño de pixel
    #print transform[5]
    
    band = ds.GetRasterBand(1) # Crea el array
    
    data = band.ReadAsArray() # Lee el array
    
    # Recorre las coordenadas de la ventana
    for point in points:
        x = point[0]
        y = point[1]
        
        # Obtiene los índices
        xOffset = int((x - xOrigin) / pixelWidth)
        yOffset = int((y - yOrigin) / pixelHeight)
        #print xOffset
        #print yOffset
        
        # Obtiene el valor individual de acuerdo a los indices
        value = data[yOffset][xOffset]
        
    return value   
 
def extraeTiff():
    """
    ==========================================================================================
    Función que extrae los valores del TIFF recortado y los convierte a un numpy array   
    ==========================================================================================
    """
    print ('Extrayendo tif...')
    
    # Extrae valores del TIFF a un numpy array
    ds = gdal.Open('tmp_4326_rec.tif')
    data = ds.ReadAsArray()
       
    # Elimina los tif temporales
    os.remove('tmp.tif')
    os.remove('tmp_4326.tif')
    
    return data

def tiempoEscaneo(path):
    """
    ==========================================================================================
	 Función que obtiene la fecha y los tiempos de escaneo a partir del nombre del archivo
    ==========================================================================================
    """
    # Busca el tiempo de inicio de escaneo
    Start = (path[path.find("s")+1:path.find("_e")])    
     
    # Busca el tiempo de finalizado de escaneo
    End = (path[path.find("e")+1:path.find("_c")])    
    
    # Le da formato al tiempo de observación    
    ano = Start[0:4]
    dia = Start[4:7]
    fecha = Start[0:14]
    horaInicio =  Start [7:9] + ":" + Start [9:11] + ":" + Start [11:13] + "." + Start [13:14] 
    horaTerminado = End [7:9] + ":" + End [9:11] + ":" + End [11:13] + "." + End [13:14]
            
    return ano,dia,horaInicio,horaTerminado,fecha

def regionCoordenadas(x,y):
    """
    ==========================================================================================
	 Función que obtiene el cuadrante de las coordenadas buscadas de acuerdo a su valor
    ==========================================================================================
    """
    # Obtiene la region de acuerdo a las coordenadas   
    if x < 0 and y > 0 :
        xNom = 'W'
        yNom = 'N'
    elif x > 0 and y > 0 :
        xNom = 'E'
        yNom = 'N'
    elif x < 0 and y < 0 :
        xNom = 'W'
        yNom = 'S'
    else : 
        xNom = 'E'
        yNom = 'S'
    
    return xNom,yNom
    
def calculaTicks(dataMin,dataMax):
    """
    ==========================================================================================
    Función que calcula los intervalos numéricos de la simbología basándose en los valores
    de la ventana recortada, estos pueden ser aumentados si se requiere
    ==========================================================================================
    """
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

def plotDatos (x,y,offset,var,path,coorven,dataVen,dataMin,dataMax,dataMean,varBus,varName,stdName,unidades,varCal,paleta,logoPath,muestraDatos):
    """
    ==========================================================================================
    Función que mapea los datos de la ventana, requiriendo el numpy array creado a partir 
    de los datos de TIFF recortado y reproyectado, además de mostrar la información de la 
    variable 
    ==========================================================================================
    """
    print ('Mapeando datos...')

    # Tamaño de la figura
    fig = plt.figure(figsize=(15,15))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax = plt.axis('off')
    
    # Crea el mapa base con las coordenadas extremas
    bmap = Basemap(llcrnrlon=coorven[0], llcrnrlat=coorven[1], urcrnrlon=coorven[2], urcrnrlat=coorven[3], resolution='i', epsg=4326) 
    bmap.drawcoastlines(linewidth=1.5)
    bmap.drawcountries(linewidth=1.5)                    
    bmap.drawstates(linewidth=0.5)
    bmap.drawparallels(np.arange(-90.0, 90.0, offset/2.0), linewidth=0.5, color='black')
    bmap.drawmeridians(np.arange(0.0, 360.0, offset/2.0), linewidth=0.5, color='black')
    
    # Plotea los datos con la paleta asignada
    bmap.imshow(dataVen, origin='upper', cmap=paleta)
    
    # Agrega una barra de color
    tick1,tick2,tick3,tick4,tick5,tick6,tick7 = calculaTicks(dataMin,dataMax)   
    
    # Agrega los valores de los intervalos a la barra de color
    cb = bmap.colorbar(location='bottom', size = '2.0%', pad = '-2.0%', ticks=[tick1,tick2,tick3,tick4,tick5,tick6,tick7])
    cb.ax.set_xticklabels([str(round(tick1,2)),str(round(tick2,2)),str(round(tick3,2)),str(round(tick4,2)),str(round(tick5,2)),str(round(tick6,2)),str(round(tick7,2))])
    cb.outline.set_visible(True) # Coloca una línea en el borde
    cb.ax.tick_params(width = 0) # Remueve los ticks
    cb.ax.xaxis.set_tick_params(pad=-20) # Pone lo valores de los intervalos dentro de la barra
    cb.ax.tick_params(axis='x', colors='black', labelsize=15) # Define el color y tamaño de la letra de los ticks
    
    # Agrega un label al punto
    label = str(round(float(varBus),3))+'\n('+str(x)+','+str(y)+')'
    
    # Agrega un marcador del punto buscado   
    estx, esty = bmap(x,y)
    bmap.plot(estx, esty, marker='+',color='r', markersize=55)
    plt.text(x+(offset/15.0), y+(offset/15.0), label, fontsize=20)

    # Obtiene las regiones de las coordenadas      
    xNom,yNom = regionCoordenadas(x,y)

    # Obtiene la fecha y los tiempos de escaneo 
    ano,dia,horaInicio,horaTerminado,fecha = tiempoEscaneo(path)   
    
    if muestraDatos == True:
	    # Agrega un rectangulo para colocar los datos
	    currentAxis = plt.gca()
	    currentAxis.add_patch(Rectangle((x-offset,  y-offset/1.04),offset*0.75 ,offset*0.11 , alpha=1, facecolor='silver', zorder = 3,ec="black", lw=1.0))
	     
	    # Agrega los datos de la variable al rectángulo 
	    plt.text(x-offset/1.02, y-offset/1.19, 'Archivo: '+path[path.find("OR"):path.find("_s")]+'...\nVariable: '+var+' '+varName+'\nNombre Estandar: '
	            +stdName+'\nUnidades: '+unidades, fontsize=12)

	    # Agrega los datos de la ventana
	    plt.text(x-offset/1.02, y-offset/1.05, 'Maximo: '+str(round(dataMax,2))+'\nMinimo:  '+str(round(dataMin,2))+'\nMedia:    '+str(round(dataMean,2)),fontsize=15)
	    
	    # Agrega los datos de la coordenada
	    plt.text(x-offset/1.38, y-offset/1.07,'\nLatitud:    '+str(abs(round(y,2)))+' '+yNom+'\nLongitud: '+str(abs(round(x,2)))+' '+xNom, fontsize=15)
	    
	    # Agrega el valor y la calidad del dato de acuerdo al subdataset DQF, que define la calidad con la que fueron calculados los datos, este se encuentra
	    # en todos los NetCDF L1b y L2 de Goes, lo define por el color de la letra
	    if varCal == 0:
	        calColor = 'g'
	        calidad = 'Algoritmo procesado'

	    elif varCal == 16 or varBus == np.nan:
	        calColor = 'b'
	        calidad = 'Algoritmo no procesado'
	    
	    else:
	        calColor = 'r'
	        calidad = 'Algoritmo con calidad: '+str(int(varCal))

	    plt.text(x-offset/2.22,  y-offset/1.09,str(round(float(varBus),2)), fontsize=30, color=calColor)
	    plt.text(x-offset/2.24,  y-offset/1.06,calidad,fontsize=7, color=calColor)
    
    # Agrega la fecha y los tiempos de escaneo.
    plt.text(x-offset/1.02,y+offset/1.25,'Fecha: '+ano+'-'+dia+'\nESCANEO\nInicio: '+horaInicio+'\nFinal: '+horaTerminado,fontsize=23)
            
    # Agrega un logo
    logo = plt.imread(logoPath)
    plt.figimage(logo,965, 19, zorder=3, alpha = 1, origin = 'upper')
    
    # Guarda y muestra el mapa
    plt.savefig('Goes16_'+var+'_'+fecha+'_'+str(abs(y))+yNom+'_'+str(abs(x))+xNom+'.png')    
    plt.show()

def plotBuscador(path,var,x,y,offset,paleta,logoPath,muestraDatos):
    """
    ==========================================================================================
    Esta es la función principal, encuentra el valor de una variable dentro de un NetCDF L1b o 
    L2 de Goes 16, obteniendo una ventana de visualización en coordenadas geográficas usando el
    módulo basemap, ademas de mostrar la calidad del dato en base a su valor dado en los datos 
    de calidad DQF.

    Usa herramientas de GDAL del sistema, incorporándolas a Python por medio del módulo os o 
    subprocess para el recorte y reproyección.
    
    Requerimientos:
    Gdal 2.3.1 o superior en su versión de escritorio. 
    
    Parámetros:
    path: es la ruta del archivo nc, ejemplo: 'OR_ABI-L2-CMIPF-M3C01_G16_s20182761800374_e20182761811141_c20182761811213.nc'
    var: es la variable del nc a buscar, se puede usar gdalinfo para conocer el nombre correcto, ejemplo: 'LST'
    x: longitud en grados decimales, con sistema de referencia EPSG:4326, ejemplo: -99.19
    y: latitud en grados decimales, con sistema de referencia EPSG:4326, ejemplo: 19.19
    offset: es la extensión de la ventana en grados desde la coordenada buscada, ejemplo: 1.0  
    paleta: el nombre de la paleta de colores predefinida por matplotlib o creada por la función loadCPT de cpt_covert, ejemplo: 'jet'
    logoPath: un logo en formato PNG de preferencia de 100X60 px, ejemplo: 'Logo.png'
    muestraDatos: si se quiere mostrar los datos de la variable, ejemplo: TRUE
    ==========================================================================================
    """
    
    # Inicio del proceso de busqueda y ploteo
    start = t.time()
    
    # Version de GDAL utilizada
    #print (subprocess.call('gdalinfo --version'))
    
    print ('1. Extrayendo variable NetCDF4')

    data,dataCal,x1,x2,y1,y2,varName,stdName,unidades = extraeNetCDF(path,var)   
    
    # Obtiene las dimensiones del array
    nx = data.shape[0]
    ny = data.shape[1]
    
    # Asigna las coordenadas extremas
    xmin, ymin, xmax, ymax = [x1,y1,x2,y2]   
    
    print ('\n2. Obteniendo datos de variable')

    # Crea el TIFF
    creaTiff(data, xmin, ymin, xmax, ymax, nx, ny )
    
    # Reproyecta el TIFF y lo recorta
    reproyectaTiff(x,y,offset)
    
    # Extrae valores del TIFF reproyectado y recortado
    dataVen = extraeTiff()

    # En caso de que el recorte haya sobrepasado la región de escaneo del Goes, al sobrante se le asigna nan  
    dataVen[dataVen == -9999.] = np.nan    

    # Obtiene los valore maximos, minimos y la media de la ventana
    dataMin = np.nanmin(dataVen)
    dataMax = np.nanmax(dataVen)
    dataMean = np.nanmean(dataVen)
    
    # Extrae el valor del TIFF de la coordenada buscada
    varBus = buscadorTif('tmp_4326_rec.tif',x,y)
   
    # Borra el TIFF temporal
    os.remove('tmp_4326_rec.tif')
    
    print ('\n3. Obteniendo dato de calidad')
    
    # Obtiene la calidad del pixel buscado    
    creaTiff(dataCal, xmin, ymin, xmax, ymax, nx, ny )
    reproyectaTiff(x,y,offset)
    extraeTiff()
    varCal = buscadorTif('tmp_4326_rec.tif',x,y)
    os.remove('tmp_4326_rec.tif')
    
    print ('\n4. Ploteando datos')
    
    # Obtiene las coordenadas extremas de la ventana
    coorven = coordenadasVentana(x,y,offset)
    
    # Plotea los datos
    plotDatos(x,y,offset,var,path,coorven,dataVen,dataMin,dataMax,dataMean,varBus,varName,stdName,unidades,varCal,paleta,logoPath,muestraDatos)
    
    # Muestra la información del proceso           
    print ('Region Mapeada en:', round(t.time() - start,4), 'segundos')
    print ('Latitud :',y)
    print ('Longitud :',x)
    print (var+' :',varBus)
        
# TEST DE LA FUNCIÓN 
cpt = loadCPT('temperature.cpt')
cpt_convert = LinearSegmentedColormap('cpt', cpt)

# Parametros requeridos
path = 'OR_ABI-L2-SSTF-M3_G16_s20180661300403_e20180661356170_c20180661400158.nc'
var = 'SST'
x = -112
y = 22
offset = 15
paleta = 'Spectral'
logoPath = 'LANOT.png'
muestraDatos = True

# Función plot buscador Goes16
plotBuscador(path,var,x,y,offset,paleta,logoPath,muestraDatos)

   