#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 16:30:59 2020

@author: urielm
"""
import os

def obtieneAnio(fecha):
    from datetime import datetime
    
    fecha = datetime.strptime(fecha,'%Y/%m/%d')
    anio = str(fecha.year)
    
    return anio    
    
def obtieneDiaJ(fecha):
    from datetime import datetime
    
    try:
        fecha = datetime.strptime(fecha,'%Y/%m/%d')    
    except ValueError:
        fecha = datetime.strptime(fecha,'%Y/%b/%d')
    diaJ = int(fecha.strftime('%j'))
    
    return diaJ
    
def descargaTrack(anio,shp,region,numEvento,nomEvento,pathOutput):
    
    # downloading with requests
    
    # import the requests library
    import requests
    import zipfile

    #anio = obtieneAnio(inicio)    
    
    url = shp   
    
    # download the file contents in binary format
    r = requests.get(url)
    
    # open method to open a file on your system and write the contents
    with open(pathOutput+region+'/'+anio+'_'+numEvento+'_'+nomEvento+".zip", "wb") as code:
        code.write(r.content)
   
    with zipfile.ZipFile(pathOutput+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'.zip', 'r') as zip_ref:
        zip_ref.extractall(pathOutput+region+'/'+anio+'_'+numEvento+'_'+nomEvento)
    
    os.remove(pathOutput+region+'/'+anio+'_'+numEvento+'_'+nomEvento+".zip")

def reproyectaTrack(anio,region,numEvento,nomEvento,pathOutputSHP,pathOutputTrack):
    import geopandas as gpd
    from glob import glob
    
    file = glob(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/*_lin.shp')
    shp = file[0].split('/')[-1]
    
    try:
        df = gpd.read_file(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp) 
    
    except ValueError:
        import json
        import fiona
        from shapely.geometry import shape 
        import pandas as pd
        
        # https://gis.stackexchange.com/questions/277231/geopandas-valueerror-a-linearring-must-have-at-least-3-coordinate-tuples
        #Read data
        collection = list(fiona.open(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,'r'))
        df1 = pd.DataFrame(collection)
        
        #Check Geometry
        def isvalid(geom):
            try:
                shape(geom)
                return 1
            except:
                return 0
        df1['isvalid'] = df1['geometry'].apply(lambda x: isvalid(x))
        df1 = df1[df1['isvalid'] == 1]
        collection = json.loads(df1.to_json(orient='records'))
        
        #Convert to geodataframe
        df = gpd.GeoDataFrame.from_features(collection)
        
        df.crs = ({'init': 'epsg:4326'})
            
    df = df.to_crs({'init': 'epsg:4326'})
    
    try: 
        os.mkdir(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento)
    except FileExistsError:
        pass
    # Renombra tipo de tormentas
    #if anio == '2017':
    df.loc[df['STORMTYPE']=='Low','STORMTYPE'] = 'Baja Presión'
    df.loc[df['STORMTYPE']=='Disturbance','STORMTYPE'] = 'Disturbio'
    df.loc[df['STORMTYPE']=='Extratropical Cyclone','STORMTYPE'] = 'Ciclón Extratropical'
    df.loc[df['STORMTYPE']=='Tropical Depression','STORMTYPE'] = 'Depresión Tropical'
    df.loc[df['STORMTYPE']=='Subtropical Depression','STORMTYPE'] = 'Depresión Subtropical'
    df.loc[df['STORMTYPE']=='Subtropical Storm','STORMTYPE'] = 'Tormenta Subtropical'
    df.loc[df['STORMTYPE']=='Tropical Wave','STORMTYPE'] = 'Onda Tropical'
    df.loc[df['STORMTYPE']=='Tropical Storm','STORMTYPE'] = 'Tormenta Tropical'
    df.loc[df['STORMTYPE']=='Hurricane1','STORMTYPE'] = 'Huracán Cat. 1'
    df.loc[df['STORMTYPE']=='Hurricane2','STORMTYPE'] = 'Huracán Cat. 2'
    df.loc[df['STORMTYPE']=='Hurricane3','STORMTYPE'] = 'Huracán Cat. 3'
    df.loc[df['STORMTYPE']=='Hurricane4','STORMTYPE'] = 'Huracán Cat. 4'
    df.loc[df['STORMTYPE']=='Hurricane5','STORMTYPE'] = 'Huracán Cat. 5'  
    df.loc[df['STORMTYPE']=='Unknown','STORMTYPE'] = 'Desconocido' 
    
    #else:
    df.loc[df['STORMTYPE']=='LO','STORMTYPE'] = 'Baja Presión'
    df.loc[df['STORMTYPE']=='DB','STORMTYPE'] = 'Disturbio'
    df.loc[df['STORMTYPE']=='EX','STORMTYPE'] = 'Ciclón Extratropical'
    df.loc[df['STORMTYPE']=='TD','STORMTYPE'] = 'Depresión Tropical'
    df.loc[df['STORMTYPE']=='SD','STORMTYPE'] = 'Depresión Subtropical'
    df.loc[df['STORMTYPE']=='SS','STORMTYPE'] = 'Tormenta Subtropical'
    df.loc[df['STORMTYPE']=='WV','STORMTYPE'] = 'Onda Tropical'
    df.loc[df['STORMTYPE']=='TS','STORMTYPE'] = 'Tormenta Tropical'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==1) ,'STORMTYPE'] = 'Huracán Cat. 1'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==2),'STORMTYPE'] = 'Huracán Cat. 2'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==3),'STORMTYPE'] = 'Huracán Cat. 3'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==4),'STORMTYPE'] = 'Huracán Cat. 4'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==5),'STORMTYPE'] = 'Huracán Cat. 5'  
    df.loc[df['STORMTYPE']=='XX','STORMTYPE'] = 'Desconocido' 
        
    df.to_file(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,driver='ESRI Shapefile')
    
def reproyectaPuntos(anio,region,numEvento,nomEvento,pathOutputSHP,pathOutputTrack):
    import geopandas as gpd
    from glob import glob
    
    file = glob(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/*_pts.shp')
    shp = file[0].split('/')[-1]
    
    try:
        df = gpd.read_file(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp) 
    
    except ValueError:
        import json
        import fiona
        from shapely.geometry import shape 
        import pandas as pd
        
        # https://gis.stackexchange.com/questions/277231/geopandas-valueerror-a-linearring-must-have-at-least-3-coordinate-tuples
        #Read data
        collection = list(fiona.open(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,'r'))
        df1 = pd.DataFrame(collection)
        
        #Check Geometry
        def isvalid(geom):
            try:
                shape(geom)
                return 1
            except:
                return 0
        df1['isvalid'] = df1['geometry'].apply(lambda x: isvalid(x))
        df1 = df1[df1['isvalid'] == 1]
        collection = json.loads(df1.to_json(orient='records'))
        
        #Convert to geodataframe
        df = gpd.GeoDataFrame.from_features(collection)
        df.crs = ({'init': 'epsg:4326'})
    
    df = df.to_crs({'init': 'epsg:4326'})
    
    try: 
        os.mkdir(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento)
    except FileExistsError:
        pass
    
    #if anio == '2017':
    df.loc[df['STORMTYPE']=='Low','STORMTYPE'] = 'Baja Presión'
    df.loc[df['STORMTYPE']=='Disturbance','STORMTYPE'] = 'Disturbio'
    df.loc[df['STORMTYPE']=='Extratropical Cyclone','STORMTYPE'] = 'Ciclón Extratropical'
    df.loc[df['STORMTYPE']=='Tropical Depression','STORMTYPE'] = 'Depresión Tropical'
    df.loc[df['STORMTYPE']=='Subtropical Depression','STORMTYPE'] = 'Depresión Subtropical'
    df.loc[df['STORMTYPE']=='Subtropical Storm','STORMTYPE'] = 'Tormenta Subtropical'
    df.loc[df['STORMTYPE']=='Tropical Wave','STORMTYPE'] = 'Onda Tropical'
    df.loc[df['STORMTYPE']=='Tropical Storm','STORMTYPE'] = 'Tormenta Tropical'
    df.loc[df['STORMTYPE']=='Hurricane1','STORMTYPE'] = 'Huracán Cat. 1'
    df.loc[df['STORMTYPE']=='Hurricane2','STORMTYPE'] = 'Huracán Cat. 2'
    df.loc[df['STORMTYPE']=='Hurricane3','STORMTYPE'] = 'Huracán Cat. 3'
    df.loc[df['STORMTYPE']=='Hurricane4','STORMTYPE'] = 'Huracán Cat. 4'
    df.loc[df['STORMTYPE']=='Hurricane5','STORMTYPE'] = 'Huracán Cat. 5'  
    df.loc[df['STORMTYPE']=='Unknown','STORMTYPE'] = 'Desconocido' 
    
    #else:
    df.loc[df['STORMTYPE']=='LO','STORMTYPE'] = 'Baja Presión'
    df.loc[df['STORMTYPE']=='DB','STORMTYPE'] = 'Disturbio'
    df.loc[df['STORMTYPE']=='EX','STORMTYPE'] = 'Ciclón Extratropical'
    df.loc[df['STORMTYPE']=='TD','STORMTYPE'] = 'Depresión Tropical'
    df.loc[df['STORMTYPE']=='SD','STORMTYPE'] = 'Depresión Subtropical'
    df.loc[df['STORMTYPE']=='SS','STORMTYPE'] = 'Tormenta Subtropical'
    df.loc[df['STORMTYPE']=='WV','STORMTYPE'] = 'Onda Tropical'
    df.loc[df['STORMTYPE']=='TS','STORMTYPE'] = 'Tormenta Tropical'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==1) ,'STORMTYPE'] = 'Huracán Cat. 1'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==2),'STORMTYPE'] = 'Huracán Cat. 2'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==3),'STORMTYPE'] = 'Huracán Cat. 3'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==4),'STORMTYPE'] = 'Huracán Cat. 4'
    df.loc[(df['STORMTYPE']=='HU') & (df['SS']==5),'STORMTYPE'] = 'Huracán Cat. 5'  
    df.loc[df['STORMTYPE']=='XX','STORMTYPE'] = 'Desconocido' 
    
    df.to_file(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,driver='ESRI Shapefile')

def reproyectaWinds(anio,region,numEvento,nomEvento,pathOutputSHP,pathOutputTrack):
    import geopandas as gpd
    from glob import glob
    
    try:
        file = glob(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/*_windswath.shp')
        shp = file[0].split('/')[-1]
        
        try:
            df = gpd.read_file(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp) 
        
        except ValueError:
            import json
            import fiona
            from shapely.geometry import shape 
            import pandas as pd
            
            # https://gis.stackexchange.com/questions/277231/geopandas-valueerror-a-linearring-must-have-at-least-3-coordinate-tuples
            #Read data
            collection = list(fiona.open(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,'r'))
            df1 = pd.DataFrame(collection)
            
            #Check Geometry
            def isvalid(geom):
                try:
                    shape(geom)
                    return 1
                except:
                    return 0
            df1['isvalid'] = df1['geometry'].apply(lambda x: isvalid(x))
            df1 = df1[df1['isvalid'] == 1]
            collection = json.loads(df1.to_json(orient='records'))
            
            #Convert to geodataframe
            df = gpd.GeoDataFrame.from_features(collection)
            df.crs = ({'init': 'epsg:4326'})
        
        df = df.to_crs({'init': 'epsg:4326'})
        
        try: 
            os.mkdir(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento)
        except FileExistsError:
            pass
           
        df.to_file(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,driver='ESRI Shapefile')
    except IndexError:
        pass
    
def trackFecha(anio,region,numEvento,nomEvento,pathOutputSHP):
    import geopandas as gpd
    from glob import glob
    
    file = glob(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/*_pts.shp')
    shp = file[0].split('/')[-1]
    
    try:
        df = gpd.read_file(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp)  
        
    except ValueError:
        import json
        import fiona
        from shapely.geometry import shape 
        import pandas as pd
        
        # https://gis.stackexchange.com/questions/277231/geopandas-valueerror-a-linearring-must-have-at-least-3-coordinate-tuples
        #Read data
        collection = list(fiona.open(pathOutputSHP+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,'r'))
        df1 = pd.DataFrame(collection)
        
        #Check Geometry
        def isvalid(geom):
            try:
                shape(geom)
                return 1
            except:
                return 0
        df1['isvalid'] = df1['geometry'].apply(lambda x: isvalid(x))
        df1 = df1[df1['isvalid'] == 1]
        collection = json.loads(df1.to_json(orient='records'))
        
        #Convert to geodataframe
        df = gpd.GeoDataFrame.from_features(collection)
        df.crs = ({'init': 'epsg:4326'})
    
    if df['MONTH'][0].isdigit() == True:      
        fechaI = str(int(df['YEAR'][0]))+'/'+str(int(df['MONTH'][0]))+'/'+str(int(df['DAY'][0]))
        fechaF = str(int(df['YEAR'][len(df)-1]))+'/'+str(int(df['MONTH'][len(df)-1]))+'/'+str(int(df['DAY'][len(df)-1]))
    else:
        fechaI = str(int(df['YEAR'][0]))+'/'+str(df['MONTH'][0])+'/'+str(int(df['DAY'][0]))
        fechaF = str(int(df['YEAR'][len(df)-1]))+'/'+str(df['MONTH'][len(df)-1])+'/'+str(int(df['DAY'][len(df)-1]))
    
    horaI = int(df['HHMM'][0][:-2])
    horaF = int(df['HHMM'][len(df)-1][:-2])
    
    return fechaI,fechaF,horaI,horaF

def trackExtencion(anio,region,numEvento,nomEvento,pathOutputTrack):
    import geopandas as gpd
    from glob import glob
    
    file = glob(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/*_pts.shp')
    shp = file[0].split('/')[-1]
    
    try:
        df = gpd.read_file(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp)    
    
    except ValueError:
        import json
        import fiona
        from shapely.geometry import shape 
        import pandas as pd
        
        # https://gis.stackexchange.com/questions/277231/geopandas-valueerror-a-linearring-must-have-at-least-3-coordinate-tuples
        #Read data
        collection = list(fiona.open(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp,'r'))
        df1 = pd.DataFrame(collection)
        
        #Check Geometry
        def isvalid(geom):
            try:
                shape(geom)
                return 1
            except:
                return 0
        df1['isvalid'] = df1['geometry'].apply(lambda x: isvalid(x))
        df1 = df1[df1['isvalid'] == 1]
        collection = json.loads(df1.to_json(orient='records'))
        
        #Convert to geodataframe
        df = gpd.GeoDataFrame.from_features(collection)
        df.crs = ({'init': 'epsg:4326'})
    
    extencion = df.total_bounds
    
    return extencion

def reproyecta(nc,variable,anio):
    from osgeo import gdal
    
    ds = gdal.Open('NETCDF:'+nc+':'+variable)    
    gdal.Warp(anio+'_tmp.tif',ds,options=gdal.WarpOptions(dstSRS='EPSG:4326'))
    
def recorta(extencion,fechaNom,productoNom,escaneo,ext,anio,numEvento,nomEvento,region,pathOutputTif):
    from osgeo import gdal
        
    ds = gdal.Open(anio+'_tmp.tif')    
    gdal.Translate(pathOutputTif+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fechaNom+'_'+escaneo+'.tif',ds,options = gdal.TranslateOptions(projWin=[extencion[0]-ext,extencion[3]+ext,extencion[2]+ext,extencion[1]-ext]))

        
def descargaDia(fs,inicio,termino,horaI,horaF,producto,productoNom,numEvento,nomEvento,anio,dia,variable,extension,ext,region,pathOutputTif):
    import numpy as np
    from datetime import datetime
               
    for hora in range(horaI,horaF):
        
        hora = "{:02d}".format(hora)   
        print('Dia: '+dia)
        print('Hora: '+hora)        
        files = np.array(fs.ls('/noaa-goes16/'+producto+'/'+anio+'/'+dia+'/'+hora+'/'))        
        
        # ===============================================================================
        # AQUIIII conatdor
        contador = 0
        # ===============================================================================
        
        for file in files:
            
        # ===============================================================================
        # AQUIIII break
        # break
            if contador == 2:
                break
            
            else:
        # ===============================================================================   
                file = str(file)
                archivo = file.split('/')[-1]
                banda = archivo.split('-')[-1].split('_')[0][-2:]
                escaneo = archivo.split('/')[-1].split('-')[-1].split('_')[0][:2]
                fecha = datetime.strptime(archivo.split('_')[3][1:-1],'%Y%j%H%M%S')
                fecha = fecha.strftime('%Y/%m/%d %H:%M:%SZ')
                fechaNom = fecha.split(' ')[0].replace('/','') + '_' + fecha.split(' ')[1].replace(':','')
                
                if banda == '13':
    
                    if ('EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fechaNom+'.tif' in os.listdir(pathOutputTif+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/')) or ('EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fechaNom+'_'+escaneo+'.tif' in os.listdir(pathOutputTif+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/') ):
                        print ('Archivo '+archivo+' ya esta descargado')
                         
                        #==============================================================================
                        contador += 1
                            
                    else:
                        print('Descargando:'+archivo)                    
                        fs.get(file, archivo)
                        print('Reproyectando:'+archivo)                    
                        reproyecta(archivo,variable,anio)
                        print('Recortando:'+archivo)                    
                        recorta(extension,fechaNom,productoNom,escaneo,ext,anio,numEvento,nomEvento,region,pathOutputTif)
                            
                        os.remove(archivo)
                        
                        #=============================================================================   
                        contador += 1


def descargaAWS(anio,producto,productoNom,variable,ext,numEvento,nomEvento,region,pathOutputTif,pathOutputSHP,pathOutputTrack):
    import s3fs
    
    # Use the anonymous credentials to access public data
    fs = s3fs.S3FileSystem(anon=True)
    
    # List contents of GOES-16 bucket.
    fs.ls('s3://noaa-goes16/')
    
    # List specific files of GOES-17 CONUS data (multiband format) on a certain hour
    # Note: the `s3://` is not required
    #files = np.array(fs.ls('/noaa-goes16/ABI-L2-CMIPF/2019/240/01/'))
    #print(files)
    
    # Download the first file, and rename it the same name (without the directory structure)
    
    #inicio = 240
    #termino = 241
    #nio = 2019
    #producto = 'ABI-L2-CMIPF'
    
    fechaI,fechaF,horaI,horaF = trackFecha(anio,region,numEvento,nomEvento,pathOutputSHP)
    
    reproyectaTrack(anio,region,numEvento,nomEvento,pathOutputSHP,pathOutputTrack)
    reproyectaPuntos(anio,region,numEvento,nomEvento,pathOutputSHP,pathOutputTrack)
    reproyectaWinds(anio,region,numEvento,nomEvento,pathOutputSHP,pathOutputTrack)
    
    inicio = obtieneDiaJ(fechaI)
    # ===============================================================================
    # AQUIIII fechaF
    termino = obtieneDiaJ(fechaI)
    
    print('Inicio',inicio)
    print('Termino',termino)
    #anio = obtieneAnio(inicio)
    
    extension = trackExtencion(anio,region,numEvento,nomEvento,pathOutputTrack)
    
    try: 
        os.mkdir(pathOutputTif+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom)
    except FileExistsError:
        pass
    
    for dia in range(inicio,termino + 1):
    
        dia = "{:03d}".format(dia) 
        
        # Dia de inicio para eventos que no empiezen a las 00:00 horas
        if dia == str(inicio):
            print('Archivos de inicio')
            # ===============================================================================
            # AQUIIII 24
            descargaDia(fs,inicio,termino,horaI,horaI+1,producto,productoNom,numEvento,nomEvento,anio,dia,variable,extension,ext,region,pathOutputTif)
            
        # Dia final para eventos que no terminen a las 24:00 horas
        elif dia == str(termino):
            print('Archivos de termino')
            descargaDia(fs,inicio,termino,0,horaF,producto,productoNom,numEvento,nomEvento,anio,dia,variable,extension,ext,region,pathOutputTif)
        
        # Dias completos entre inicio y temino del evento
        else:
            print('Archivos de intermedio')
            descargaDia(fs,inicio,termino,0,24,producto,productoNom,numEvento,nomEvento,anio,dia,variable,extension,ext,region,pathOutputTif)
    try:        
        os.remove(anio+'_tmp.tif')
    except FileNotFoundError:
        pass

'''         
#inicio = '2018/10/20'
#termino = '2018/10/24'
producto = 'ABI-L2-CMIPF'
variable = 'CMI'
ext = 4
numEvento = '12'
nomEvento = 'Adrian'
anio = '2017'

pathOutputTrack = './data_track/'
pathOutputTif = './data_tif/'

descargaTrack(anio,numEvento,nomEvento,pathOutputTrack)
extension = trackExtencion(anio,numEvento,nomEvento,pathOutputTrack)
descargaAWS(anio,producto,variable,ext,pathOutputTif,pathOutputTrack)
'''
'''
import pandas as pd

df = pd.read_csv('./data_csv/eventosTropicales_DGRU.csv')

for anio,eve,nombre,tipo_cic,region,shp,pdf,kmz in zip(df['anio'],df['evento'],df['nombre'],df['tipo_cic'],df['region'],df['url_SHP'],df['url_PDF'],df['url_KMZ']):
    #if anio == 2017:
    print('Año:',anio)
    print('Numero evento:',"{:02d}".format(eve))
    print('Nombre:',nombre)
    print('Tipo ciclon:',tipo_cic)
    print('Region:',region)
    print('Shapefile:',shp)
    print('PDF:',pdf)
    print('KMZ:',kmz)
    
    producto = 'ABI-L2-CMIPF'
    variable = 'CMI'
    ext = 4
    numEvento = "{:02d}".format(eve)
    nomEvento = nombre
    region = region
    ani = str(anio)
    pathOutputSHP = './data_shp/'
    pathOutputTif = './data_tif/'
    pathOutputTrack = './data_track/'
    
    descargaTrack(ani,shp,numEvento,nomEvento,pathOutputSHP)
    extension = trackExtencion(ani,numEvento,nomEvento,pathOutputSHP)
    descargaAWS(ani,producto,variable,ext,numEvento,nomEvento,region,pathOutputTif,pathOutputSHP,pathOutputTrack)   
'''
