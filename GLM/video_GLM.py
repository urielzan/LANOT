#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 17:02:23 2019

@author: lanot
"""

import os
from glob import glob

#scale='1080'
scale='720'

def copiaArchivos(path):
    os.system('cd '+path+';cp *.jpg video')

def renombra(path): 
    path = path + '/video/'
    i = 0
    archivos = glob(path+'*.jpg')
    archivos.sort()
    #print archivos
          
    for filename in archivos: 
        dst ="img" + str(i) + ".jpg"
        #print dst
        src = filename
        #print src
        dst =path + dst
        #print dst
          
        # rename() function will 
        # rename all the files 
        os.rename(src, dst) 
        i += 1
        
def convert(path):    
    path = path + '/video'
    #os.system("cd "+path+";ffmpeg -framerate 50 -r 50 -i img%1d.jpg -an -vcodec libx264 -vf scale=-1:2070 -y lastest.mp4")
    os.system("cd "+path+";ffmpeg -framerate 100 -pattern_type sequence -i img%1d.jpg -an -vcodec libx264 -r 100 -pix_fmt yuv420p -profile:v baseline -level 3 -vf scale=-1:"+scale+" -crf 30 -y lastest.mp4") 

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

path = '/data1/output/glm/images/conus'

#borraInter(path)
copiaArchivos(path)
renombra(path)
convert(path)
borraIma(path)
copiaVideo(path)
