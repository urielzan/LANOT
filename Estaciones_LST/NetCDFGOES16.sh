#Extrael el ultimo NetCDF4

server="urielm@132.247.103.174"
dirIn="/data/output/abi/l2/conus"
dirOut="/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Estaciones_LST/data_GOES16/LST"
NC=`ssh $server 'ls -t '$dirIn'/*LST* | head -1'`
echo $NC
scp $server:$NC $dirOut

#ls -t *CMI*C01* | head -1