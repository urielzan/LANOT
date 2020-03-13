#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 17:46:29 2019
@author: lanot
"""

import glob
from osgeo import gdal
import numpy as np

from datetime import datetime

def escribeMetadatoNC(evento,productoNom,escaneo,region,anio,nomEvento,fechaInicio,eventoDGRU,fechaFinal,pathInputMeta):
   
    evento.naming_authority = 'gov.nesdis.noaa'
    #evento.Conventions = 'CF-1.7'
    evento.Metadata_Conventions = 'Unidata Dataset Discovery v1.0'
    #evento.standard_name_vocabulary = 'CF Standard Name Table (v25, 05 July 2013)'
    evento.institution = 'UNAM/LANOT/DGRU > Universidad Nacional Autónoma de México, Laboratorio Nacional de Observación de la Tierra , Dirección General de Repositorios Universitarios'  
    evento.project  = 'Colección de eventos LANOT/DGRU'
    evento.production_site = 'LANOT'
    evento.spatial_resolution = '2km al nadir'   
    evento.orbital_slot = 'GOES-Test'
    evento.platform_ID = 'G16'
    evento.instrument_type = 'GOES R Series Advanced Baseline Imager'
    #evento.scene_id = region
    evento.instrument_ID = 'FM1'
    evento.dataset_name = nomEvento+'.nc' 
    evento.title = 'Eventos DGRU/LANOT, '+eventoDGRU+', '+', '+anio+', '+nomEvento+', '+productoNom+', '+fechaInicio.strftime("%Y-%m-%dT%H:%M:%SZ")+', '+fechaFinal.strftime("%Y-%m-%dT%H:%M:%SZ")
    evento.summary = open(pathInputMeta+'sumary_ABI_CMI_C13','r').read()
    evento.license = 'Datos sin clasificar'
    evento.processing_level = 'National Aeronautics and Space Administration (NASA) L2'
    evento.date_created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    evento.cdm_data_type = 'Imagen'
    evento.time_coverage_start = fechaInicio.strftime("%Y-%m-%dT%H:%M:%SZ")
    evento.time_coverage_end = fechaFinal.strftime("%Y-%m-%dT%H:%M:%SZ")
    if escaneo == 'M3':
        evento.timeline_id = 'A cada 15 min'
    elif escaneo == 'M6':
        evento.timeline_id = 'A cada 10 min'
    elif escaneo == 'M4':
        evento.timeline_id = 'A cada 5 min'
    evento.production_data_source = 'Tiempo real'
    evento.id = 'EVENTOS_DGRU/LANOT_'+eventoDGRU.upper()+'_'+anio+'_'+nomEvento.upper()+'_'+productoNom.upper()+'_'+fechaInicio.strftime("%Y-%m-%dT%H:%M:%SZ")+'_'+fechaFinal.strftime("%Y-%m-%dT%H:%M:%SZ")

def defineDimesionesNC(evento,nx,ny):
    evento.createDimension('x',nx)
    evento.createDimension('y',ny)
    evento.createDimension('time',None)    
    evento.createDimension('nv',2)

def defineMetaVarNC(var,tipo,unidades,lngName,stdNAme):
    var.units = unidades
    var.long_name = lngName
    var.standard_name = stdNAme
    
    if tipo == 'lon':    
        var.axis = 'X'
        var.vertices = 'x_vertices'
    elif tipo == 'lat':    
        var.axis = 'Y'
        var.vertices = 'y_vertices'
    elif tipo == 'time':
        var.axis = 'T'
        var.calendar = 'gregorian'
    elif tipo == 'variable':
        var.coordinates = 'y x'
        var.setncattr('grid_mapping', 'spatial_ref')

def defineMetaSysRefNC(varCRS):
    varCRS.grid_mapping_name = 'latitude_longitude'
    varCRS.longitude_of_prime_meridian = 0.0
    varCRS.semi_major_axis = 6378137.0
    varCRS.inverse_flattening = 298.257223563
    varCRS.geographic_coordinate_system_name = "WGS 84"
    varCRS.horizontal_datum_name = "WGS_1984"
    varCRS.reference_ellipsoid_name = "WGS 84"
    varCRS.spatial_ref = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    
def obtieneNdimFechEsc(archivos):
    try:
        fechaInicio = datetime.strptime(archivos[0].split('_')[-3]+archivos[0].split('_')[-2],'%Y%m%d%H%M%SZ')
        fechaFinal = datetime.strptime(archivos[-1].split('_')[-3]+archivos[-1].split('_')[-2],'%Y%m%d%H%M%SZ')
    except ValueError:
        fechaInicio = datetime.strptime(archivos[0].split('_')[-2]+archivos[0].split('_')[-1].split('.')[0],'%Y%m%d%H%M%SZ')
        fechaFinal = datetime.strptime(archivos[-1].split('_')[-2]+archivos[-1].split('_')[-1].split('.')[0],'%Y%m%d%H%M%SZ')
    #escaneo = archivos[0].split('/')[0].split('_')[-1].split('.')[0]
    #escaneo = 'M3'

    ds = gdal.Open(archivos[0])
    nx = ds.GetRasterBand(1).XSize
    ny = ds.GetRasterBand(1).YSize    
    ds = None
    
    return fechaInicio,fechaFinal,nx,ny

def obtieneExtension(ds):    
    #[lllon,urlat,urlon,lllat]  
    geo = ds.GetGeoTransform()
    xmin = geo[0]
    ymax = geo[3]
    resx = geo[1]
    resy = geo[5]
    
    nx = ds.GetRasterBand(1).XSize
    ny = ds.GetRasterBand(1).YSize
    
    xmax = xmin + resx*nx
    ymin = ymax + resy*ny
    extension = [xmin,ymax,xmax,ymin]
    
    return extension
        
def plotRGB(data,extension,imagen,fechaInicio,fechaFinal,fecha,anio,region,numEvento,nomEvento,tipoCiclon,productoNom,productoMapa,pathOutputPNG,pathOutputMap,pathOutputTrack):
    import os
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    #import matplotlib.image as image
    from cpt_convert import loadCPT # Import the CPT convert function
    from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
    #import matplotlib.ticker as mticker
    import cartopy.crs as crrs
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import geopandas as gpd
    from glob import glob
    from PIL import Image
    #import cartopy.feature as cfeature
    #from matplotlib.lines import Line2D
    #from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    # Es X
    dimMapY = (extension[2]-extension[0])/445000
    #print("AQUIIIIIX",dimMapY)
    #dimMapX = (extension[1]-extension[3])/445000
    #print("AQUIIIIIX",dimMapY)
    #print("AQUII2",dimMapX)
    
    #print('EXTENCION',dimMapX,dimMapY)
    
    fechaNom = fecha.split(' ')[0].replace('/','') + '_' + fecha.split(' ')[1].replace(':','')
    
    if 'EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fecha+".png" in os.listdir(pathOutputPNG+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/'):
        print ('Archivo EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fecha+".png"+' ya esta creado')
    else:
                    
        cpt = loadCPT('./paletas/IR4AVHRR6.cpt')
        cpt_convert = LinearSegmentedColormap('cpt', cpt)
        
        fig = plt.figure(figsize=((extension[2]-extension[0])/445000,(extension[1]-extension[3])/445000))
        ax = plt.axes([0,0,1,1],projection=crrs.Mercator(),frameon=False)
    
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)    
        plt.autoscale(tight=True) 
        plt.gca().outline_patch.set_visible(False)
          
        ax.set_extent([extension[0],extension[2],extension[3],extension[1]], crs=crrs.Mercator())
        plt.imshow(data,extent=[extension[0],extension[2],extension[3],extension[1]],vmin = -103.15,vmax = 104.85,cmap=cpt_convert)
                        
        plt.savefig(pathOutputPNG+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fechaNom+".png",dpi=300,bbox_inches='tight', pad_inches=0)
      
        # =========================================================
        # Ploteo de mapa de trayectoria    
        #plt.suptitle(tipoCiclon+' '+nomEvento, y=dimMapY/5)
        plt.title(fechaInicio.strftime(tipoCiclon.upper()+' '+nomEvento.upper()+'\n'+'%Y/%m/%dT%H:%M:%SZ')+'  -  '+fechaFinal.strftime('%Y/%m/%dT%H:%M:%SZ')
        +'\n'+productoMapa,fontsize=dimMapY*1.4,color="black")    
        #grids
        gl = ax.gridlines(crs=crrs.PlateCarree(), draw_labels=True,linewidth=dimMapY/10, color='black', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': dimMapY, 'color': 'black'}
        gl.ylabel_style = {'size': dimMapY, 'color': 'black'}
        #elemnts
        file = glob(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/*_lin.shp')
        shp_track = file[0].split('/')[-1]    
        df_track = gpd.read_file(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp_track) 
        df_track = df_track.to_crs({'init':'epsg:3857'})
        df_track.plot(ax=ax,column='STORMTYPE', linewidth = dimMapY/5, cmap='tab20',legend = True,legend_kwds={'loc': 'lower right','fontsize':dimMapY,'title':'Estado','title_fontsize':dimMapY,'borderpad':0.1,'handletextpad':0.1,'markerscale':dimMapY/10,'shadow':False,'edgecolor':'none'})
        #for i in range(len(df_track)):
            #if df_track.iloc(i)['STORMTYPE'] == 'Baja Presión':                        
        #df_track.plot(ax=ax,column='STORMTYPE', linewidth = dimMapY/5, color=['#FF0000', '#FF6C00', '#FFEC00', '#B6FF00', '#64FF00', '#14BC00', '#4AFFB2', '#00FFE4', '#00AEFF', '#00AEFF','#0065EE','#5A49FF','#AF49FF','#FF00E0'],legend = True,legend_kwds={'loc': 'lower right','fontsize':dimMapY,'title':'Estado','title_fontsize':dimMapY,'borderpad':0.1,'handletextpad':0.1,'markerscale':dimMapY/10,'shadow':False,'edgecolor':'none'})
        
        file = glob(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/*_pts.shp')
        shp_pts = file[0].split('/')[-1]    
        df_pts = gpd.read_file(pathOutputTrack+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/'+shp_pts) 
        df_pts = df_pts.to_crs({'init':'epsg:3857'})
        df_pts.plot(ax=ax,color='black',markersize=dimMapY/11,zorder=2)
        props = dict(boxstyle='round', facecolor='white',edgecolor='none', alpha=0.7)
        for x, y, label,label1 in zip(df_pts.geometry.x, df_pts.geometry.y, df_pts.HHMM,df_pts.DAY):
            if label == '1200':
                ax.annotate(label, xy=(x, y), xytext=(dimMapY*0.6, dimMapY*0.6), textcoords="offset points",fontsize=dimMapY/1.5,bbox=props)
            if label == '0000':
                ax.annotate(int(label1), xy=(x, y), xytext=(dimMapY*0.6, dimMapY*1.4), textcoords="offset points",fontsize=dimMapY*0.9,color='r',bbox=props)
        
        #ax.add_feature(cfeature.LAND)
        #ax.coastlines(linewidth=dimMapY/16,resolution='10m')            
        df_enti = gpd.read_file('./shapefiles/coastlines_mexicoMer/coastlines_mexicoMer.shp')
        #df_enti = df_enti.to_crs({'init':'epsg:3857'})
        #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        df_enti.plot(ax=ax,color = 'black',linewidth=0.3)
        #props = dict(boxstyle='round', facecolor='white',edgecolor='none', alpha=0.7)
        plt.text(extension[0]+dimMapY*5500,extension[3]+dimMapY*8000 ,fecha,color = 'black',fontsize=dimMapY*1.6,bbox=props)
        #ax.imshow(logo,extent=[extension[0],extension[2],extension[3],extension[1]])
        
        plt.imshow(data,extent=[extension[0],extension[2],extension[3],extension[1]],vmin = -103.15,vmax = 104.85,cmap=cpt_convert)
        #cax = fig.add_axes([0.001,0.99, 0.998, 0.01])
        #if dimMapY > dimMapX:
         #   dimcb = dimMapX
        #else:
         #   dimcb = dimMapY
        # dimcb*0.0019097747932542944
        cax = fig.add_axes([0.001,0.99,0.998,0.01])
        cbar = plt.colorbar( cax=cax, orientation='horizontal')
        cbar.ax.tick_params(labelsize=dimMapY, grid_alpha=0.5)
        cbar.outline.set_linewidth(dimMapY/15)
        #cbar.outline.set_linewidth(0)
        plt.savefig(pathOutputMap+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fechaNom+".png",dpi=300,bbox_inches='tight', pad_inches=0)
        
        logo = Image.open('./logos/lanot_logo.png')
        logo = logo.resize((int(dimMapY*37),int(dimMapY*11)), Image.ANTIALIAS)
        mapa = Image.open(pathOutputMap+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fechaNom+".png")
        mapa.paste(logo,(int(mapa.width)-int((dimMapY*40)),int(dimMapY*3)),logo)
        mapa.save(pathOutputMap+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'_'+fechaNom+".png")
        
        fig.clear()
        ax.clear()
        plt.close(fig)
        #plt.close(ax)
    
def obtienePNG(ds,timeDim_cont,fechaInicio,fechaFinal,fecha,anio,region,numEvento,nomEvento,tipoCiclon,productoNom,productoMapa,pathOutputPNG,pathOutputMap,pathOutputTrack):
    import os
    gdal.Warp(anio+'_tmp_mer.tif',ds,options=gdal.WarpOptions(dstSRS='EPSG:3857'))
    ds_mer = gdal.Open(anio+'_tmp_mer.tif')
    scaleFactor_mer = float(ds_mer.GetRasterBand(1).GetMetadata_Dict()['scale_factor']) 
    addOffset_mer = float(ds_mer.GetRasterBand(1).GetMetadata_Dict()['add_offset'])         
    data_mer = ds_mer.ReadAsArray()    
    data_mer = data_mer * scaleFactor_mer + addOffset_mer                
    data_mer = data_mer - 273.15                   
    extension_mer = obtieneExtension(ds_mer)
    plotRGB(data_mer,extension_mer,timeDim_cont,fechaInicio,fechaFinal,fecha,anio,region,numEvento,nomEvento,tipoCiclon,productoNom,productoMapa,pathOutputPNG,pathOutputMap,pathOutputTrack)    
    ds_mer = None
    os.remove(anio+'_tmp_mer.tif')

def creaEventoNC(nomEvento,region,productoNom,productoMapa,eventoDGRU,tipoCiclon,anio,numEvento,pathOutputTif,pathOutputNC,pathOutputPNG,pathOutputMap,pathOutputTrack,pathInputMeta):
    from netCDF4 import Dataset
    import os
    #import numpy.ma as ma
    
    archivos = glob.glob(pathOutputTif+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/*.tif')
    archivos.sort()
    
    fechaInicio,fechaFinal,nx,ny = obtieneNdimFechEsc(archivos)
    
    escaneo = archivos[0].split('/')[-1].split('_')[-1].split('.')[0]
    
    print(fechaInicio,fechaFinal,escaneo)
    
    if 'EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+".nc" in os.listdir(pathOutputNC+region+'/'):
        print ('Archivo EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+".nc"+' ya esta creado')
                        
    else:        
        try: 
            os.mkdir(pathOutputPNG+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom)
        except FileExistsError:
            pass
        try: 
            os.mkdir(pathOutputMap+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom)
        except FileExistsError:
            pass
        
        evento = Dataset(pathOutputNC+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+".nc",'w')
        
        escribeMetadatoNC(evento,productoNom,escaneo,region,anio,nomEvento,fechaInicio,eventoDGRU,fechaFinal,pathInputMeta)
        
        defineDimesionesNC(evento,nx,ny)
        
        lon = evento.createVariable('x',np.float32,('x',),fill_value = -9999.0)
        defineMetaVarNC(lon,'lon','grados_Este','longitud','longitud') 
        
        lat = evento.createVariable('y',np.float32,('y',),fill_value = -9999.0)
        defineMetaVarNC(lat,'lat','grados_Norte','latitud','latitud')    
        
        time = evento.createVariable('time',np.float32,('time',),fill_value = -9999.0)
        # 'hours since 2017-9-5 00:00:00'
        defineMetaVarNC(time,'time','minutes since '+fechaInicio.strftime("%Y-%m-%d %H:%M:00"),'time','time') 
            
        cmi = evento.createVariable('CMI',np.float32,('time','y','x'),fill_value = -9999.0)
        defineMetaVarNC(cmi,'variable','grados_Celsius','ABI L2+ Cloud and Moisture Imagery brightness temperature','toa_brightness_temperature') 
        
        lon_vertices = evento.createVariable('x_vertices',np.float32,('nv'),fill_value = -9999.0)
        defineMetaVarNC(lon_vertices,None,'grados_Este','Coordenadas en X oeste/este de la extensión de la imagen','vertices_longitud')
        
        lat_vertices = evento.createVariable('y_vertices',np.float32,('nv'),fill_value = -9999.0)
        defineMetaVarNC(lat_vertices,None,'grados_Norte','Coordenadas en Y sur/norte de la extensión de la imagen','vertices_latitud')
        
        crs = evento.createVariable('spatial_ref', 'i4')
        defineMetaSysRefNC(crs)
          
        #coor = [-135,45,-15,-20]
        #coor2 = [-120,36,-52,1]pathOutputTif
        
        timeDim_cont = 0
        time_cont = 0
        timeList = []
        
        for archivo in archivos:    
            print('Leyendo archivo:' + archivo)
            
            escaneo = archivo.split('/')[-1].split('_')[-1].split('.')[0]
            
            ds = gdal.Open(archivo)        
            scaleFactor = float(ds.GetRasterBand(1).GetMetadata_Dict()['scale_factor']) 
            addOffset = float(ds.GetRasterBand(1).GetMetadata_Dict()['add_offset'])         
            data = ds.ReadAsArray()
            #data = np.where(data == -1 , np.nan, data)        
            data = data * scaleFactor + addOffset                
            data = data - 273.15      
            #ma.set_fill_value(data, -9999.0)
            #data[data == -9999.0] = np.nan
            #data[data >= 0.0] = np.nan
                
            print ('Añadiendo archivo '+str(timeDim_cont+1)+':'+archivo)
                   
            data_f = np.flipud(data)           
            
            cmi[timeDim_cont:timeDim_cont+1,:,:] = data_f
            time[timeDim_cont] = time_cont
            timeList.append(time_cont)
            
            timeDim_cont = timeDim_cont + 1
            if escaneo == 'M3':
                time_cont = time_cont + 15
            elif escaneo == 'M6':
                time_cont = time_cont + 10
            elif escaneo == 'M4':
                time_cont = time_cont + 5
            extension = obtieneExtension(ds)
           
            # Obtencion de png
            try:
                fecha = datetime.strptime(archivo.split('_')[-3]+archivo.split('_')[-2],'%Y%m%d%H%M%SZ')
            except ValueError:
                fecha = datetime.strptime(archivo.split('_')[-2]+archivo.split('_')[-1].split('.')[0],'%Y%m%d%H%M%SZ')                
            fecha = fecha.strftime('%Y/%m/%d %H:%M:%SZ')
            obtienePNG(ds,timeDim_cont,fechaInicio,fechaFinal,fecha,anio,region,numEvento,nomEvento,tipoCiclon,productoNom,productoMapa,pathOutputPNG,pathOutputMap,pathOutputTrack)
            
            if 'Z_M' in archivo:
                os.rename(archivo,archivo[:archivo.find('Z_M')+1]+'.tif')
            
        #timeList = np.asarray(timeList, dtype=np.float32)
        #ma.set_fill_value(timeList, -9999)
        #time = timeList
        
        resx = ds.GetGeoTransform()[1]
        resy = ds.GetGeoTransform()[5]
        
        #lonVert_min = ds.GetGeoTransform()[0]
        #lonVert_max = ds.GetGeoTransform()[0]+resx*(data.shape[1])
        #latVert_min = ds.GetGeoTransform()[3]+resy*(data.shape[0])
        #latVert_max = ds.GetGeoTransform()[3]
        #archivo[:-3]
        lonVert_min = extension[0]
        lonVert_max = extension[2]
        latVert_min = extension[3]
        latVert_max = extension[1]
        
        #coor2 = [-120,36,-52,1]
        x =  np.linspace(lonVert_min,lonVert_max,nx)
        #ma.set_fill_value(x, -9999.0)
        evento.variables['x'][:] = x
    
        y =  np.linspace(latVert_min,latVert_max,ny)
        #ma.set_fill_value(y, -9999.0)
        evento.variables['y'][:] = y
        
        evento.variables['CMI'].resolution ='y:'+str(resy)+' grados x:'+str(resx)+' grados'
            
        evento.variables['x_vertices'][:] = [lonVert_min,lonVert_max]
        evento.variables['y_vertices'][:] = [latVert_min,latVert_max]
        
        evento.close()
        ds = None

'''  
eventoDGRU = 'Ciclones Tropicales/Húracan'
tipoCiclon = 'Húracan'
region = 'Pácifico'
producto = 'ABI-L2-CMI-C13'
productoMapa = 'GOES-16/ABI CMI Banda 13 (10.3 µm) Temperatura C°'
nomEvento = 'Arlene'
anio = '2017'
numEvento = '01'

pathInputMeta = './data_metadato/'

pathOutputTif = './data_tif/'
pathOutputNC = './data_nc/'
pathOutputPNG = './data_png/'
pathOutputMap = './data_map/'
pathOutputTrack = './data_track/'

creaEventoNC(nomEvento,region,producto,productoMapa,eventoDGRU,tipoCiclon,anio,numEvento,pathOutputTif,pathOutputNC,pathOutputPNG,pathOutputMap,pathOutputTrack)

'''
