#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:40:30 2019

@author: urielm
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from glob import glob

files = glob('./data/*.csv')
files.sort()

df = pd.read_csv('data/incendios_20191210000.csv')
df.insert(6,"time",0)


time = 1
times = []

for file in files:
    
    jday = file[file.find('2019')+4:file.find('.csv')-4]
    
    if jday == '121':
    
        df1 = pd.read_csv(file) 
        df1.insert(6,"time",1)
        df1['time'] = time
        
        df = pd.concat([df,df1])
          
       
        times.append(time)
        
        time = time + 1



df["geometry"] = df.apply(lambda x: Point(x["lng"], x["lat"]) , axis = 1)

gdf = gpd.GeoDataFrame(df, geometry='geometry',crs={'init': 'epsg:4326'})

gdf.to_file("output.json", driver="GeoJSON")