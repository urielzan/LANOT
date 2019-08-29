#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 14:09:01 2019

@author: lanot
"""

import glob
import os

archivos = glob.glob('./*OR*.nc')
archivos.sort()

for i in archivos:
    if not i[i.find('_s')+11:i.find('_s')+13] == '00':
        print 'Eliminando: '+i
        os.remove(i)
    


