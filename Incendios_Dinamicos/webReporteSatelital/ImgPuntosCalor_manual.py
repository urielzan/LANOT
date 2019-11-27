#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 13:29:32 2019

@author: lanot
"""
import matplotlib
matplotlib.use('Agg')
import dataPuntosCalor,dataGOES16,dataSuomiNPP,dataSentinel2

import GOES16,SuomiNPP,Sentinel2

import ensamble_manual

#import numpy as np

import os

def manual(x,y):
	dataGOES16.borraTodo()
	dataSuomiNPP.borraTodo()
	dataSentinel2.borraTodo()

	path = '/home/incendios/IncendiosDinamicos/'

	pathPuntosCalor = path+'data_PuntosCalor/'
	pathGOES16 = path+'data_GOES16/'
	pathSuomiNPP = path+'data_SuomiNPP/'
	pathSentinel2 = path+'data_Sentinel2/'

#if len(os.listdir('/var/www/incendios'))>2:
 #   os.system('rm /var/www/incendios/*.jpg*')
  #  os.system('rm /var/www/incendios/*.txt')

#os.remove('/home/incendios/IncendiosDinamicos/output/*')
#os.system('mv /var/www/html/incendios/* /home/lanot/Documents/IncendiosIma')
#csv,puntos,coordenadas,csvArchivo,fechaPC,puntos,puntosMexico = dataPuntosCalor.PuntosCalor(pathPuntosCalor)
    
#info = 'Archivo CSV: '+csvArchivo+'\n'+'Fecha CSV: '+fechaPC+'\n'+'Puntos de Calor Detectados: ',str(puntos),'\n'+'Puntos de Calor Depurados: ',str(puntosMexico),'\n'+'\n'+'\n'+'lon,lat,tmpFinPC'
#infoArchivo = open('/var/www/incendios/info_'+csvArchivo[:-3]+'txt','a')
#infoArchivo.writelines(info)
#infoArchivo.close()

#if len(coordenadas['lon']) == 0:
    
#    print(csv)    
#    print ("No se detectaron incendios ")
#    infoArchivo.write('\nNo se detectaron incendios ')
#    infoArchivo.close()
#else:
#infoArchivo.close()       
#dataPuntosCalor.plotPuntos(coordenadas['lon'],coordenadas['lat'])

	dataGOES16.extraeNetCDF()
	dataSuomiNPP.extraeGTiff()
#os.system('mv /var/www/incendios/* /home/incendios/Resultados')

#ESTO ES NUEVO, RECORTES MAS RAPIDOS.
	archivosG16 = GOES16.archivosGOES16(pathGOES16)
	print (archivosG16)

	b7,xmin,ymin,xmax,ymax,nx,ny = GOES16.extraeNetCDFL2(archivosG16[5],2)
	GOES16.creaTiff(b7,xmin,ymin,xmax,ymax,nx,ny,'b7')
	GOES16.reproyectaG16('b7')

	b6,xmin,ymin,xmax,ymax,nx,ny = GOES16.extraeNetCDFL2(archivosG16[4],2)    
	GOES16.creaTiff(b6,xmin,ymin,xmax,ymax,nx,ny,'b6')
	GOES16.reproyectaG16('b6')

	b5,xmin,ymin,xmax,ymax,nx,ny = GOES16.extraeNetCDFL2(archivosG16[3],2)
	GOES16.creaTiff(b5,xmin,ymin,xmax,ymax,nx,ny,'b5')
	GOES16.reproyectaG16('b5')

	b3,xmin,ymin,xmax,ymax,nx,ny = GOES16.extraeNetCDFL2(archivosG16[1],1)    
	GOES16.creaTiff(b3,xmin,ymin,xmax,ymax,nx,ny,'b3')
	GOES16.reproyectaG16('b3')

	b2,xmin,ymin,xmax,ymax,nx,ny = GOES16.extraeNetCDFL2(archivosG16[2],1)    
	GOES16.creaTiff(b2,xmin,ymin,xmax,ymax,nx,ny,'b2')
	GOES16.reproyectaG16('b2')

	b1,xmin,ymin,xmax,ymax,nx,ny = GOES16.extraeNetCDFL2(archivosG16[0],1)
	GOES16.creaTiff(b1,xmin,ymin,xmax,ymax,nx,ny,'b1')
	GOES16.reproyectaG16('b1')


 #   for x,y in zip(coordenadas['lon'],coordenadas['lat']):
        
  #      try: 

	print ("\nProcesando Coordenada: ",x,',',y)
	x = float(x)
	y = float(y)
	#infoArchivo = open('/var/www/incendios/info_'+csvArchivo[:-3]+'txt','a')

	offsetGOES16 = 1
	offsetSuomiNPP = 0.5
	offsetSentinel2 = 0.1

	dataSentinel2.extraeWMS(x,y,offsetSentinel2,'1-NATURAL-COLOR,DATE','TC_',pathSentinel2,'TC')
	dataSentinel2.extraeWMS(x,y,offsetSentinel2,'91_SWIR,DATE','SWIR_',pathSentinel2,'SWIR')

	G16_TC_imagen,G16_FT_imagen = GOES16.RGBGoes16(pathGOES16,x,y,offsetGOES16)
	SNPP_TC_imagen,SNPP_FT_imagen,paso = SuomiNPP.RGBSuomiNPPI(pathSuomiNPP,x,y,offsetSuomiNPP)
	Sen2_TC_imagen = Sentinel2.RGBSentilen2(x,y,offsetSentinel2,'TC',pathSentinel2,'Sentinel2_TC_')
	Sen2_SWIR_imagen = Sentinel2.RGBSentilen2(x,y,offsetSentinel2,'SWIR',pathSentinel2,'Sentinel2_SWIR_')

	fechaG16 = dataGOES16.revisaNetCDF('1')
	if paso == 1:        
	    fechaSNPP = dataSuomiNPP.revisaGTif('03','19')
	else:
	    fechaSNPP = dataSuomiNPP.revisaGTif('03','18')

	#QUITAR ESTO
	tmpPC = '2019'

	logo_path = 'logo.jpg'
	ubiMun_path = 'ubicacion_muni.png'
	ubiEnt_path = 'ubicacion_edo.png'
	imgF = ensamble_manual.ensambleSat(x,y,G16_TC_imagen,G16_FT_imagen,SNPP_TC_imagen,SNPP_FT_imagen,Sen2_TC_imagen,Sen2_SWIR_imagen,ubiMun_path,ubiEnt_path,logo_path,tmpPC,fechaG16,fechaSNPP)

	#infoArchivo.write('\n'+str(x)+','+str(y)+','+str(tmpPC))
	#infoArchivo.close()


	os.remove(G16_TC_imagen)
	os.remove(G16_FT_imagen)
	os.remove(SNPP_TC_imagen)
	os.remove(SNPP_FT_imagen)
	os.remove(Sen2_TC_imagen)
	os.remove(Sen2_SWIR_imagen)
	os.remove('ubicacion_edo.png')
	os.remove('ubicacion_muni.png')
	os.remove('tmp_rec.tif.aux.xml')
	os.remove('tmp_4326_rec.tif.aux.xml')
	            
	#except:
	#print ("Incendio fuera de rango")

	#diaPC = 
	#horaPC = csvArchivo[-8:-4]

	#os.system('mkdir /home/incendios/Resultados/'+diaPC+'/'+horaPC+'/Imagenes_G16_SNPP_S2')
	#os.system('cp /var/www/incendios/*.jpg /home/incendios/Resultados/'+diaPC+'/'+horaPC+'/Imagenes_G16_SNPP_S2')
	#os.system('cp /var/www/incendios/*.txt /var/www/incendios/PC_txt')
	#os.system('cp /var/www/incendios/*.txt /home/incendios/Resultados/'+diaPC+'/'+horaPC+'/Imagenes_G16_SNPP_S2')

	dataGOES16.borraTodo()
	dataSuomiNPP.borraTodo()
	dataSentinel2.borraTodo()
	os.remove('b7_tmp.tif')    
	os.remove('b6_tmp.tif')
	os.remove('b5_tmp.tif')
	os.remove('b3_tmp.tif')
	os.remove('b2_tmp.tif')
	os.remove('b1_tmp.tif')
	os.remove('b7_tmp_4326.tif')
	os.remove('b6_tmp_4326.tif')    
	os.remove('b5_tmp_4326.tif')
	os.remove('b3_tmp_4326.tif')
	os.remove('b2_tmp_4326.tif')
	os.remove('b1_tmp_4326.tif')
	#infoArchivo.close()
	os.system('rm /home/incendios/IncendiosDinamicos/output/*')
	
	return imgF

#lon = -99
#lat = 19

#manual(lon,lat)
