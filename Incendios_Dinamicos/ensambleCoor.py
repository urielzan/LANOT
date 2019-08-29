#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 13:50:29 2019

@author: lanot
"""

from PIL import Image,ImageDraw,ImageFont
import ubicacionCoor

def creaBase():
    #base = Image.new('RGB', (10698, 5332), color = '#2E2E2E')
    base = Image.new('RGB', (10698, 5332), color = 'white')
    datosBase = Image.new('RGB', (3500, 4832), color = '#676767')  
    
    return base,datosBase

def extImagenes(G16_TC_path,G16_FT_path,SNPP_TC_path,SNPP_FT_path,Sen2_TC_path,Sen2_SWIR_path,ubiMun_path,ubiEnt_path,logo_path):
    
    G16_TC = Image.open(G16_TC_path)
    G16_FT = Image.open(G16_FT_path)
    SNPP_TC = Image.open(SNPP_TC_path)
    SNPP_FT = Image.open(SNPP_FT_path)
    Sen2_TC = Image.open(Sen2_TC_path)
    Sen2_SWIR = Image.open(Sen2_SWIR_path)
    
    ubiMun = Image.open(ubiMun_path)
    ubiEdo = Image.open(ubiEnt_path)
    
    logo = Image.open(logo_path)

    return G16_TC,G16_FT,SNPP_TC,SNPP_FT,Sen2_TC,Sen2_SWIR,ubiMun,ubiEdo,logo

def pegaImagenes(base,datosBase,G16_TC,G16_FT,SNPP_TC,SNPP_FT,Sen2_TC,Sen2_SWIR,ubiMun,ubiEnt,logo):
    
    #base.paste(datosBase,(7148,300))
    G16_TC = G16_TC.crop((10,10,G16_TC.width-10,G16_TC.height-10))
    G16_FT = G16_FT.crop((10,10,G16_FT.width-10,G16_FT.height-10))
    SNPP_TC = SNPP_TC.crop((10,10,SNPP_TC.width-10,SNPP_TC.height-10))
    SNPP_FT = SNPP_FT.crop((10,10,SNPP_FT.width-10,SNPP_FT.height-10))
    Sen2_TC = Sen2_TC.crop((10,10,Sen2_TC.width-10,Sen2_TC.height-10))
    Sen2_SWIR = Sen2_SWIR.crop((10,10,Sen2_SWIR.width-10,Sen2_SWIR.height-10))
    
    base.paste(G16_TC, (50,300))
    base.paste(G16_FT, (50,2816))
    base.paste(SNPP_TC, (2416,300))
    base.paste(SNPP_FT, (2416,2816))
    base.paste(Sen2_TC, (4782,300))
    base.paste(Sen2_SWIR, (4782,2816))
    
    ubiMun = ubiMun.resize((1280,1250), Image.ANTIALIAS)
    ubiEnt = ubiEnt.resize((3494,2316), Image.ANTIALIAS)
    
    ubiEnt = ubiEnt.crop((10,10,ubiEnt.width-10,ubiEnt.height-10))
    ubiMun = ubiMun.crop((1,1,ubiMun.width-1,ubiMun.height-1))
    
    base.paste(ubiEnt,(7148,300))
    base.paste(ubiMun,(9375,300),ubiMun)
    
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
    
    coorFor = str("%0.2f" % abs(round(x,2)))+' '+xNom+' '+str("%0.2f" % abs(round(y,2)))+' '+yNom
    
    return coorFor

def aditexto(base,muni,enti,nomMuni,nomEnt,cveMun,cveEnt,cveGeo,coorFor,fechaG16,fechaSNPP):
    
    font = ImageFont.truetype('gadugi-2.ttf',size=150)
    satelite = ImageDraw.Draw(base)
    satelite.text((500,50), "GOES-16/Sensor ABI",font=font,fill='black')
    satelite.text((2750,50), "Suomi-NPP/Sensor VIIRS",font=font,fill='black')
    satelite.text((5200,50), "Sentinel-2/Sensor MSI",font=font,fill='black')
    satelite.text((8450,50), "UBICACIÓN",font=font,fill='black')

    font = ImageFont.truetype('gadugi-2.ttf',size=80)
    compuesto = ImageDraw.Draw(base)
    compuesto.text((185,2650),"True Color [C01(0.47 um),C02(0.64 um),C03(0.86 um)]",font=font,fill='black')
    compuesto.text((2600,2650),"True Color [C03(0.48 um),C04(0.55 um),C05(0.67 um)]",font=font,fill='black')
    compuesto.text((5000,2650),"True Color [C02(0.49 um),C03(0.55 um),C04(0.66 um)]",font=font,fill='black')
    compuesto.text((185,5160),"Fire Temperature [C05(1.6 um),C06(2.25 um),C07(3.9 um)]",font=font,fill='black')
    compuesto.text((2550,5160),"Fire Temperature [C10(1.61 um),C11(2.25 um),C12(3.7 um)]",font=font,fill='black')
    compuesto.text((5100,5160),"SWIR [C03(0.55 um),C8A(0.83 um),C12(2.2 um)]",font=font,fill='black')
        
    font = ImageFont.truetype('gadugi-2.ttf',size=125)
    puntoCalor = ImageDraw.Draw(base)
    puntoCalor.text((7950,2700),'Punto de Calor GOES-16 detectado',font=font,fill='black')
    puntoCalor.text((8275,2725),'\n2019-01-07 12:30 GMT',font=font,fill='black')
        
    font = ImageFont.truetype('gadugi-2.ttf',size=250)
    coordenada = ImageDraw.Draw(base)
    coordenada.text((8025,3000),coorFor,font=font,fill='black')
    
    font = ImageFont.truetype('gadugi-2.ttf',size=120)
    ubica = ImageDraw.Draw(base)
    ubica.text((7180,3400),'LOCALIZACIÓN\nMunicipio:\nEntidad:\nClave Municipio:\nClave Entidad:\nClave Geoestadística:',font=font,fill='black')
    ubica.text((9000,3400),'\n'+nomMuni+'\n'+nomEnt+'\n'+cveMun+'\n'+cveEnt+'\n'+cveGeo,font=font,fill='black')
    
    font = ImageFont.truetype('gadugi-2.ttf',size=120)
    tiempos = ImageDraw.Draw(base)
    tiempos.text((7180,4400),'TIEMPO DE ESCANEO\nGOES-16/ABI:\nSuomi-NPP/VIIRS\nSentinel-2/MSI',font=font,fill='black')
    tiempos.text((9000,4400),'\n'+fechaG16+' GMT\n'+fechaSNPP+' GMT\n-',font=font,fill='black')
    
def ensambleSat(x,y,G16_TC_path,G16_FT_path,SNPP_TC_path,SNPP_FT_path,Sen2_TC_path,Sen2_SWIR_path,ubiMun_path,ubiEnt_path,logo_path,fechaG16,fechaSNPP):
    
    muni,enti,nomMuni,nomEnt,cveMun,cveEnt,cveGeo = ubicacionCoor.ubicaPuntosCalor(x,y)
    
    base,datosBase = creaBase()
    
    G16_TC,G16_FT,SNPP_TC,SNPP_FT,Sen2_TC,Sen2_SWIR,ubiMun,ubiEdo,logo = extImagenes(G16_TC_path,G16_FT_path,SNPP_TC_path,SNPP_FT_path,Sen2_TC_path,Sen2_SWIR_path,ubiMun_path,ubiEnt_path,logo_path)
        
    print G16_TC.width,G16_TC.height
    print ubiEdo.width,ubiEdo.height
    
    pegaImagenes(base,datosBase,G16_TC,G16_FT,SNPP_TC,SNPP_FT,Sen2_TC,Sen2_SWIR,ubiMun,ubiEdo,logo)
    
    coorFor = regionCoordenadas(x,y)
    aditexto(base,muni,enti,nomMuni,nomEnt,cveMun,cveEnt,cveGeo,coorFor,fechaG16,fechaSNPP)
    
    base.save('/var/www/html/pruebas/Prueba_'+str(x)+'_'+str(y)+'.png')
    
    base = None
    datosBase = None
