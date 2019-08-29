#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 15:35:37 2019

@author: lanot
"""

import os
from multiprocessing import Pool

os.system('export PATH=/home/lanotadm/bin:$PATH')

pathInput='/data1/output/abi/l2/fd'
pathOutput='/data/goes16/abi/l2/geotiff'

# Script generico de productos L2
script_1 = 'ncToGeoTiff_L2.py'

# Casos especiales
script_2 = 'ncToGeoTiff_uaem.py'

# Procesos de productos L2 de CSPP
# Formato:
# 'script' 'Directorio' 'Producto' 'Variable' 'EPSG' 'Resolucion' 'Clave de rescortes del archivo recortes_coordenadas.csv'  

#=========================================================================================================
# AEROSOL
processes_1 = script_1+" "+pathInput+" "+pathOutput+"'/aerosol' 'ADP' 'Aerosol' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_2 = script_1+" "+pathInput+" "+pathOutput+"'/aerosol' 'ADP' 'Dust' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_3 = script_1+" "+pathInput+" "+pathOutput+"'/aerosol' 'ADP' 'Smoke' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_4 = script_1+" "+pathInput+" "+pathOutput+"'/aerosol' 'AOD' 'AOD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
#=========================================================================================================

#=========================================================================================================
# CLOUD
processes_5 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'ACM' 'BCM' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_6 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'CODD' 'COD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_7 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'CODN' 'COD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_8 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'CPSD' 'PSD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_9 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'CPSN' 'PSD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_10 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'ACHA' 'HT' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_11 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'ACTP' 'Phase' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_12 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'CTP' 'PRES' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
processes_13 = script_1+" "+pathInput+" "+pathOutput+"'/cloud' 'ACHT' 'TEMP' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
#=========================================================================================================

#=========================================================================================================
# LST
processes_14 = script_1+" "+pathInput+" "+pathOutput+"'/lst' 'LST' 'LST' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local'"
# Caso especial de LST en celsius
processes_15 = script_2+" "+pathInput+" "+pathOutput+"'/lst' 'LST' 'LST' '4326' '2km' 'mexico'"
#=========================================================================================================

#=========================================================================================================
# NAV

#==========================================================================================================

# Tupla de procesos que entraran a la ejecucion paralela
processes = (processes_1,processes_2,processes_3,processes_4,processes_5,processes_6,processes_7,processes_8,processes_9,processes_10,processes_11,
processes_12,processes_13,processes_14,processes_15)

#for i in processes:
#	print ('python3 {}'.format(i))

def run_process(process):
    os.system('{}'.format(process))

pool = Pool(processes=len(processes))
pool.map(run_process, processes)
