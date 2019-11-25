# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""
from dataSentinel2 import extraeWMS
from flask import Flask,request,redirect,url_for,render_template


app = Flask(__name__)

@app.route('/',methods=["GET", "POST"])
def hello():
    
    if request.method == 'POST':
        #lat = 19.0
        #lon = -99.63
        
        lon = request.form['lon']
        lat = request.form['lat']

        offset = 0.05
        path = 'static'
        
        imageWMS = extraeWMS(lon,lat,offset,'1-NATURAL-COLOR,DATE','TC_',path,'TC')
        
        #extraeWMS(lon,lat,offset,'2_COLOR_INFRARED__VEGETATION_,DATE','FC_',path,'FC')
        #extraeWMS(lon,lat,offset,'91_SWIR,DATE','SWIR_',path,'SWIR')
        #extraeWMS(lon,lat,offset,'5_VEGETATION_INDEX,DATE','NDVI_',path,'NDVI')

    return render_template('index.html',image = imageWMS)

if __name__ == "__main__":
    app.run()