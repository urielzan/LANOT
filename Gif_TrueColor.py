# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 17:26:48 2018

@author: LANOT02
"""

import os
import imageio



outputPath = 'C:\\Users\\LANOT02\\Desktop\\Prueba_TrueColor\\output_FD_trueColor\\'

images = []
for file_name in os.listdir(outputPath):
    if file_name.endswith('.png'):
        file_path = os.path.join(outputPath, file_name)
        images.append(imageio.imread(file_path))
        
imageio.mimsave('C:\\Users\\LANOT02\\Desktop\\Prueba_TrueColor\\output_FD_trueColor\\Animacion', images, duration = 0.05)
print ("Listo GIF!!!")
