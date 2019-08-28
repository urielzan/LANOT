!/bin/bash

# Manda a llamar el script ncToGeoTiff_L2 para cada producto en paralelo

# Directorios 
pathInput='/data1/output/abi/l2/fd'
pathOutput='/data/goes16/abi/l2/geotiff'

# Aerosol
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/aerosol' 'ADP' 'Aerosol' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/aerosol' 'ADP' 'Dust' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/aerosol' 'ADP' 'Smoke' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/aerosol' 'AOD' 'AOD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &

# Cloud
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'ACM' 'BCM' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'CODD' 'COD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'CODN' 'COD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'CPSD' 'PSD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'CPSN' 'PSD' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'ACHA' 'HT' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'ACTP' 'Phase' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'CTP' 'PRES' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/cloud' 'ACHT' 'TEMP' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &

# LST
python3 ncToGeoTiff_L2.py $pathInput $pathOutput'/lst' 'LST' 'LST' '4326' '2km' 'a1,a2,a3,a4,a5,mexico,centroam,local' &
# Caso especial de UAEM LST en Celsius
python3 ncToGeoTiff_uaem.py $pathInput $pathOutput'/lst' 'LST' 'LST' '4326' '2km' 'mexico' &

# NAV


