#-*- coding: utf-8 -*-
"""
Created on Sun Feb  3 00:07:44 2019

@author: on_de
"""
#import matplotlib
#matplotlib.use("Agg")

import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import cartopy.crs as crrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

def coordenadasVentana(x,y,offset):
    print ('Obteniendo coordenadas ventana...')    

    # Obtiene las coordenadas extremas de la ventana de acuerdo al offset
    urlon = x + offset
    lllon = x - offset        
      
    urlat = y + offset
    lllat = y - offset
    
    coorVentana = [lllon,urlat,urlon,lllat]    
    return coorVentana

def extSatelites(x,y):
    G16 = coordenadasVentana(x,y,1)
    SNPP = coordenadasVentana(x,y,0.5)
    Sen2 = coordenadasVentana(x,y,0.1)
    
    return G16,SNPP,Sen2

def datosCoor(x,y,shpMuni,shpEnti):
    
    coord = Point(x,y)
    
    global muni
    global enti
    global nomMuni
    global nomEnt
    global cveMun
    global cveEnt
    global cveGeo
    
    for i in range(len(shpMuni)):
        try:
            if shpMuni['geometry'][i].contains(coord) == True:
                muni = i
                nomMuni = shpMuni['NOM_MUN'][i]
                nomEnt = shpMuni['NOM_ENT'][i]
                cveMun = shpMuni['CVE_MUN'][i]
                cveEnt = shpMuni['CVE_ENT'][i]
                cveGeo = shpMuni['CVEGEO'][i]
              
                
        except:
            print ("Incendio fuera de Rango")
            #muni = 1
            #nomMuni = shpMuni['NOM_MUN'][1]
            #nomEnt = shpMuni['NOM_ENT'][1]
            #cveMun = shpMuni['CVE_MUN'][1]
            #cveEnt = shpMuni['CVE_ENT'][1]
            #cveGeo = shpMuni['CVEGEO'][1]
                
    for i in range(len(shpEnti)):
        try:
            if shpEnti['geometry'][i].contains(coord) == True:
                enti = i
        
        except:
            print ("Incendio fuera de Mexico")         
          
    return muni,enti,nomMuni,nomEnt,cveMun,cveEnt,cveGeo

def plotUbicaMuni(shpMuni,muni,nomMuni,x,y):
    f, ax = plt.subplots(1, figsize=(15, 10))
    
    #ax.patch.set_facecolor('#2E2E2E')    
    
    ax.axis('off')
    ax = plt.axes(projection=crrs.PlateCarree())
    #ax.background_patch.set_facecolor('#939393')
    ax = shpMuni.plot(axes=ax,color='#939393',linewidth=1,edgecolor='#2E2E2E')
    #ax.coastlines()
    ax.set_extent([x-0.3,x+0.3,y-0.3,y+0.3])     
                                      
    gl = ax.gridlines(draw_labels=True,linewidth=0.5, color='black', alpha=0.8, linestyle='--')
    
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 13, 'color': 'black'}
    gl.ylabel_style = {'size': 13, 'color': 'black','rotation':'vertical'}
    
    try:
        if len(shpMuni['geometry'][muni]) > 1:
            for i in range(len(shpMuni['geometry'][muni])):
                plt.fill(shpMuni['geometry'][muni][i].exterior.xy[0],shpMuni['geometry'][muni][i].exterior.xy[1],'#535353')
    
    except :
        plt.fill(shpMuni['geometry'][muni].exterior.xy[0],shpMuni['geometry'][muni].exterior.xy[1],'#535353')
    
    plt.plot(x,y,'r.',markersize=20,label='Punto de calor')
    ax.legend(loc='lower left',fontsize=18,facecolor='white')
    #plt.text(x+0.008,y+0.008,'['+str(round(x,2))+','+str(round(y,2))+']',fontsize=10,fontname = 'gadugi',color='black')
    plt.text(shpMuni['geometry'][muni].centroid.x-0.05,shpMuni['geometry'][muni].centroid.y,nomMuni.upper(),fontsize=18,fontname = 'gadugi',color='black')
    
    plt.savefig('ubicacion_muni.png',transparent=True,dpi=300,bbox_inches='tight',pad_inches=0)

def plotUbicaEdo(shpEnti,enti,nomEnt,G16,SNPP,Sen2):

    f, ax = plt.subplots(1, figsize=(15, 10),frameon=False)

    ax.axis('off')
                                      
    ax = plt.axes(projection=crrs.PlateCarree())
    #ax.background_patch.set_facecolor('#2E2E2E')
    ax.background_patch.set_facecolor('white')
    ax.set_extent([-119,-78,11.5,35.5]) 
    #ax = shpEnti.plot(axes=ax,color='#939393',linewidth=0.5,edgecolor='#2E2E2E')
    ax = shpEnti.plot(axes=ax,color='#939393',linewidth=0.5,edgecolor='white')
    ax.set_axis_off()
    
    try:
        if len(shpEnti['geometry'][enti]) > 1:
            for i in range(len(shpEnti['geometry'][enti])):
                plt.fill(shpEnti['geometry'][enti][i].exterior.xy[0],shpEnti['geometry'][enti][i].exterior.xy[1],'#535353')
    
    except :
        plt.fill(shpEnti['geometry'][enti].exterior.xy[0],shpEnti['geometry'][enti].exterior.xy[1],'#535353')
    
    plt.fill([G16[0],G16[2],G16[2],G16[0],G16[0]],[G16[3],G16[3],G16[1],G16[1],G16[3]],'b',alpha=0.5,label='GOES-16 / ABI')
    plt.fill([SNPP[0],SNPP[2],SNPP[2],SNPP[0],SNPP[0]],[SNPP[3],SNPP[3],SNPP[1],SNPP[1],SNPP[3]],'r',alpha=0.5,label='Suomi-NPP / VIIRS')
    plt.fill([Sen2[0],Sen2[2],Sen2[2],Sen2[0],Sen2[0]],[Sen2[3],Sen2[3],Sen2[1],Sen2[1],Sen2[3]],'y',alpha=0.5,label='Sentinel-2 / MSI')
    ax.legend(loc='lower left',facecolor='white',fontsize=18)
    #plt.plot(x,y,'r.',markersize=3)
    #plt.text(-118.75,34,nomEnt.upper(),fontsize=28,fontname = 'gadugi',color='white')
    
    plt.savefig('ubicacion_edo.png',dpi=300,bbox_inches='tight',pad_inches=0)

def ubicaPuntosCalor(x,y): 

    shpEnti = gpd.read_file('/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/dest2018gw/dest2018gw.shp')
    shpMuni = gpd.read_file('/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/muni_2018gw/muni_2018gw.shp')

    muni,enti,nomMuni,nomEnt,cveMun,cveEnt,cveGeo = datosCoor(x,y,shpMuni,shpEnti)
    
    G16,SNPP,Sen2 = extSatelites(x,y)
    plotUbicaMuni(shpMuni,muni,nomMuni,x,y)
    plotUbicaEdo(shpEnti,enti,nomEnt,G16,SNPP,Sen2)
    
    return muni,enti,nomMuni,nomEnt,cveMun,cveEnt,cveGeo

#x = -106.13
#y = 25.87

#muni,enti,nomMuni,nomEnt,cveMun,cveEnt,cveGeo = ubicaPuntosCalor(x,y)

#print nomMuni
#print nomEnt
#print cveMun
#print cveEnt
#print cveGeo
