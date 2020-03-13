#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 17:02:23 2019
@author: urielm
"""

import os
from glob import glob

def copiaArchivos(pathInput,pathOutputVideo):
    os.system('cd '+pathInput+';cp *.png '+pathOutputVideo)

def renombra(pathOutputVideo): 
    #path = path + '/video/'
    i = 0
    archivos = glob(pathOutputVideo+'*.png')
    archivos.sort()
    #print archivos
          
    for filename in archivos: 
        dst = str(i) + ".png"
        #print dst
        src = filename
        #print src
        dst =pathOutputVideo + dst
        #print dst
          
        # rename() function will 
        # rename all the files 
        os.rename(src, dst) 
        i += 1
        
def convert(pathInput,pathOutputVideo,scale,region,numEvento,nomEvento,productoNom,anio):    
    #os.system("cd "+path+";ffmpeg -framerate 50 -r 50 -i img%1d.jpg -an -vcodec libx264 -vf scale=-1:2070 -y lastest.mp4")
    #try:
    #    os.mkdir(pathOutputVideo+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/')
    #except FileExistsError:
    #    pass
    
    if 'EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+".mp4" in os.listdir(pathOutputVideo+region+'/'):
        print ('Archivo EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+".mp4"+' ya esta creado')
    else:
        #os.mkdir(pathOutputVideo+region+'/'+anio+'_'+numEvento+'_'+nomEvento+'/')
        copiaArchivos(pathInput+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+'/',pathOutputVideo+region+'/')
        renombra(pathOutputVideo+region+'/')
        #TEMPORAL========================================================
        #os.chdir(pathOutputVideo+region+'/')
        os.system("cd "+pathOutputVideo+region+'/'+";ffmpeg -framerate 25 -pattern_type sequence -i %1d.png -an -vcodec libx264 -r 100 -pix_fmt yuv420p -profile:v baseline -level 3 -vf scale=-2:"+scale+" -crf 30 -y "+pathOutputVideo+region+'/EDL_CT_'+anio+'_'+numEvento+'_'+nomEvento+'_'+productoNom+".mp4")
        os.system('rm '+pathOutputVideo+region+'/'+'*.png')

def borraIma(path):
    path = path + '/video'
    os.system('rm '+path+'/*.jpg')

def copiaVideo(path):
    path = path + '/video'
    os.system('cp '+path+'/*.mp4 /var/www/html/animations/glm')

def borraInter(path):
    archivos_video = glob(path+'/*.jpg')
    archivos_video.sort()
    archivos_video_h = archivos_video[:32]
    for j in archivos_video_h:
        os.system('rm '+j)

'''
nomL = ['Arlene','Bret']
numL = ['01','02']
scale='1500'
#scale='720'
#nomEvento = 'Arlene'
#numEvento = '01'
anio = '2017'
region = 'Atlántico'

pathInputPNG = './data_png/'
pathInputMap = './data_map/'
pathOutputVideo = '/home/urielm/Documents/EVENTOS_DGRU_LANOT/eventoNC/pruebaScript/scripts/data_video/'

#borraInter(path)
#copiaArchivos(path)
#renombra(path)
#convert(pathInputPNG,pathOutputVideo,scale,region,numEvento,nomEvento,anio)
for nomEvento,numEvento in zip(nomL,numL):
    print(nomEvento)
    convert(pathInputMap,pathOutputVideo,scale,region,numEvento,nomEvento,anio)
#borraIma(path)
#copiaVideo(path)

'''
