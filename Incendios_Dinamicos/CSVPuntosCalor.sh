#Extrael el ultimo CSV

server="lanot04@132.247.103.184"
dirIn="/home/lanot04/datos_terrama2/puntos_goes"
dirOut="/home/lanot/Documents/Scripts_Tesis/Scripts_Tesis/Incendios_Dinamicos/data_PuntosCalor"
CSV=`ssh $server 'ls -t '$dirIn' | head -1'`
#echo $CSV
scp $server:$dirIn'/'$CSV $dirOut



#ls -t *CMI*C01* | head -1