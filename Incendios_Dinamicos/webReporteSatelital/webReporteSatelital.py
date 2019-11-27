# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""
from ImgPuntosCalor_manual import manual
from dataSentinel2_manual import extraeWMS
from flask import Flask,request,render_template,url_for


app = Flask(__name__)

@app.route('/ReporteSatelital',methods=["GET", "POST"])
def ReporteSatelital():
    imageWMS='static/latest.png'
    if request.method == 'POST':
        #lat = 19.0
        #lon = -99.63
        
        lon = request.form['lon']
        lat = request.form['lat']
        #offset = float(request.form['offset'])

        #composite = request.form['composite']
        
        #print (composite)
        #offset = 0.05
        path = 'static/'
        
        imageWMS = manual(lon,lat)
        #imageWMS = extraeWMS(lon,lat,offset,'2_COLOR_INFRARED__VEGETATION_,DATE','FC_',path,'FC')
        
        #extraeWMS(lon,lat,offset,'2_COLOR_INFRARED__VEGETATION_,DATE','FC_',path,'FC')
        #extraeWMS(lon,lat,offset,'91_SWIR,DATE','SWIR_',path,'SWIR')
        #extraeWMS(lon,lat,offset,'5_VEGETATION_INDEX,DATE','NDVI_',path,'NDVI')

    return render_template('ReporteSatelital.html',image = imageWMS)

@app.route('/ReporteSentinel2',methods=["GET", "POST"])
def ReporteSentinel2():
    imageWMS='latest.png'
    if request.method == 'POST':
        #lat = 19.0
        #lon = -99.63

        lon = request.form['lon']
        lat = request.form['lat']
        offset = float(request.form['offset'])

        composite = request.form['composite']

        #print (composite)
        #offset = 0.05
        path = 'static/'

        imageWMS = extraeWMS(lon,lat,offset,composite,'FC_',path,'FC')
        #imageWMS = extraeWMS(lon,lat,offset,'2_COLOR_INFRARED__VEGETATION_,DATE','FC_',path,'FC')

        #extraeWMS(lon,lat,offset,'2_COLOR_INFRARED__VEGETATION_,DATE','FC_',path,'FC')
        #extraeWMS(lon,lat,offset,'91_SWIR,DATE','SWIR_',path,'SWIR')
        #extraeWMS(lon,lat,offset,'5_VEGETATION_INDEX,DATE','NDVI_',path,'NDVI')

    return render_template('ReporteSentinel2.html',image = imageWMS)

@app.route('/')
def menu():

    return render_template('index.html')



if __name__ == "__main__":
    app.run(host = '132.247.103.186',port=5000)
