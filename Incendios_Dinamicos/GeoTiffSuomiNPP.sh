#Extrael el ultimo NetCDF4

server="ilma@132.247.103.150"
dirIn="/nexus/trex/products/geotiff/Global/viirs/level1"
dirOut="/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_SuomiNPP/C"$1
GTIF1=`ssh $server 'ls -t '$dirIn'/*.19*ch'$1'.SVM.* | head -1'`
GTIF2=`ssh $server 'ls -t '$dirIn'/*.18*ch'$1'.SVM.* | head -1'`
GTIF3=`ssh $server 'ls -t '$dirIn'/*.20*ch'$1'.SVM.* | head -1'`
echo $GTIF1
echo $GTIF2
echo $GTIF3
scp $server:$GTIF1 $dirOut
scp $server:$GTIF2 $dirOut
scp $server:$GTIF3 $dirOut

#ls -t *CMI*C01* | head -1

