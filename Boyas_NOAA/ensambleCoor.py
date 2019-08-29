#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 13:50:29 2019

@author: lanot
"""

from PIL import Image,ImageDraw,ImageFont
import ubicacionCoor

def creaBase():
    #base = Image.new('RGB', (8500, 5000), color = '#2E2E2E')
    base = Image.new('RGB', (8500, 5000), color = 'white')                 
    #datosBase = Image.new('RGB', (3500, 4832), color = '#676767')  
    
    return base#,datosBase

def extImagenes(Sen2_TC_LST_path,grafica_path,ubiMun_path,ubiEnt_path,logo_path):
    
    
    Sen2_TC_LST = Image.open(Sen2_TC_LST_path)
    grafica = Image.open(grafica_path)
    
    ubiMun = Image.open(ubiMun_path)
    ubiEdo = Image.open(ubiEnt_path)
    
    logo = Image.open(logo_path)

    return Sen2_TC_LST,grafica,ubiMun,ubiEdo,logo

def pegaImagenes(base,Sen2_TC_LST,grafica,ubiMun,ubiEnt,logo):
    
    #base.paste(datosBase,(7148,300))
   
    Sen2_TC_LST = Sen2_TC_LST.crop((10,10,Sen2_TC_LST.width-10,Sen2_TC_LST.height-10))
    Sen2_TC_LST = Sen2_TC_LST.resize((4900,4900), Image.ANTIALIAS)    
    base.paste(Sen2_TC_LST, (50,50))
    
    grafica = grafica.resize((3400,2500), Image.ANTIALIAS)
    base.paste(grafica,(5000,2600))
   
    ubiEnt = ubiEnt.crop((10,10,ubiEnt.width-10,ubiEnt.height-10))
    #ubiMun = ubiMun.crop((1,1,ubiMun.width-1,ubiMun.height-1)) 
    #ubiMun = ubiMun.resize((1100,1100), Image.ANTIALIAS)
    ubiEnt = ubiEnt.resize((2900,1900), Image.ANTIALIAS)      
    base.paste(ubiEnt,(5550,50))
    #base.paste(ubiMun,(7350,450),ubiMun)
    
    #logo = logo.resize((500,250),Image.ANTIALIAS)
    #base.paste(logo,(10100,5000))

def regionCoordenadas(x,y):   
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
    
    lat = str("%0.2f" % abs(round(y,2)))+' '+yNom
    lon = str("%0.2f" % abs(round(x,2)))+' '+xNom    
    return [lon,lat]

def aditexto(base,coorFor,estacion,ubicacion,altitud):
    
    font = ImageFont.truetype('gadugi-2.ttf',size=100)
    satelite = ImageDraw.Draw(base)    
    satelite.text((1400,50), "Sentinel-2(TRUE COLOR)/Suomi-NPP(SST)",font=font,fill='white')
    satelite.text((6500,50), "UBICACION",font=font,fill='black')
    
    font = ImageFont.truetype('gadugi-2.ttf',size=80)
    ubica = ImageDraw.Draw(base)
    #ubica.text((5300,2100),'LOCALIZACION\nMunicipio:\nEntidad:\nClave Municipio:\nClave Entidad:\nClave Geoestadistica:',font=font)
    #ubica.text((6200,2100),'\n'+nomMuni+'\n'+nomEnt+'\n'+cveMun+'\n'+cveEnt+'\n'+cveGeo,font=font)
    ubica.text((5300,2100),'DATOS BOYA NOAA\nBoya:\nUbicacion:\nProfundidad:\nLongitud:\nLatitud:',font=font,fill='black')
    ubica.text((6200,2100),'\n'+estacion+'\n'+ubicacion+'\n'+str(altitud)+'\n'+coorFor[0]+'\n'+coorFor[1],font=font,fill='black')
            
#def ensambleSat(x,y,Sen2_TC_LST_path,grafica_path,ubiMun_path,ubiEnt_path,logo_path,salida_path,estacion,ubicacion,operador,altitud):
def ensambleSat(x,y,Sen2_TC_LST_path,grafica_path,ubiMun_path,ubiEnt_path,logo_path,salida_path,estacion,ubicacion,altitud):
    ubicacionCoor.ubicaPuntosCalor(x,y)
    
    base = creaBase()
    
    Sen2_TC_LST,grafica,ubiMun,ubiEdo,logo = extImagenes(Sen2_TC_LST_path,grafica_path,ubiMun_path,ubiEnt_path,logo_path)
        
    print Sen2_TC_LST.width,Sen2_TC_LST.height
    print ubiEdo.width,ubiEdo.height
    
    pegaImagenes(base,Sen2_TC_LST,grafica,ubiMun,ubiEdo,logo)
    
    coorFor = regionCoordenadas(x,y)
    aditexto(base,coorFor,estacion,ubicacion,altitud)
    
    base.save(salida_path+'BNOAA_SST_'+str(x)+'_'+str(y)+'.png')
    
    base = None

#x = -87
#y = 22
#Sen2_TC_LST_path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/output/SuomiNPP_SST_-87_22.png'
#salida_path = '/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Boyas_SST/salida/'
#estacion = '01'
#ubicacion = 'Caca'
#operador = 'chabelo'
#altitud = 'bubu'
#grafica_path = 'grafica.png'
#ubiMun_path = 'ubicacion_muni.png'
#ubiEnt_path = 'ubicacion_edo.png'
#logo_path = 'LANOT.png'
#fechaG16 = '2019/02/12 12:30'

#ensambleSat(x,y,Sen2_TC_LST_path,grafica_path,ubiMun_path,ubiEnt_path,logo_path,salida_path,estacion,ubicacion,operador,altitud)
