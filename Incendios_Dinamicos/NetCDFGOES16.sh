#Extrael el ultimo NetCDF4

server="urielm@132.247.103.174"
dirIn="/data/output/abi/l2/conus"
dirOut="/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_GOES16/C0"$1
NC=`ssh $server 'ls -t '$dirIn'/*CMI*C0'$1'* | head -1'`
echo $NC
scp $server:$NC $dirOut

#ls -t *CMI*C01* | head -1