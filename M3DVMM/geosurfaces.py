from geoseismo import surface_3d
#Superficies geológicas

Eoceno=surface_3d('./datasets/DISCORDANCIA_EOCENO.txt','#FDA75F','#9d4702','Discordancia del Eoceno Medio',1)
Colorado=surface_3d('./datasets/TOPE_COLORADO.txt','#FEC07A','#d06f01','Tope Formación Colorado',1)
Mugrosa=surface_3d('./datasets/TOPE_MUGROSA.txt','#ffa46b','#b34400','Tope Formación Mugrosa',1)
Chorros=surface_3d('./datasets/TOPE_CHORROS.txt','#FDB46C','#974d02','Tope Grupo Chorros',1)
Real=surface_3d('./datasets/BASE_CUATERNARIO.txt','#FFFF00','#adad00','Tope Grupo Real',1)

paja=surface_3d('./datasets/PAJA_SGC_TVDSS_3.xyz','#8CCD57','#8CCD57','Formación Paja',2)
salada=surface_3d('./datasets/SALADA_SGC_TVDSS_3.xyz','#BFE35D','#BFE35D','Formación Salada',2)
simiti=surface_3d('./datasets/SIMITI_SGC_TVDSS_3.xyz','#BFE48A','#BFE48A','Formación Simiti',2)
galembo=surface_3d('./datasets/GALEMBO_SGC_TVDSS_3.xyz','#E6F47F','#E6F47F','Formación Galembo',2)

ciraShale=surface_3d('./datasets\Capas Kale_Base_CiraShale.csv','#FFE619','#FFE619','Cira Shale',2)
bagre=surface_3d('./datasets\Capas Kale_Fm_Bagre.csv','#FFFF00','#FFFF00','Formación Bagre',2)
chontorales=surface_3d('./datasets\Capas Kale_Fm_Chontorales.csv','#FFFF00','#FFFF00','Formación Chontorales',2)
colorado=surface_3d('./datasets\Capas Kale_Fm_Colorado.csv','#FEE6AA','#FEE6AA','Formación Colorado',2)
enrejado=surface_3d('./datasets\Capas Kale_Fm_Enrejado.csv','#FFFF00','#FFFF00','Formación Enrejado',2)
esmeraldas=surface_3d('./datasets\Capas Kale_Fm_Esmeraldas.csv','#FDCDA1','#FDCDA1','Formación Esmeraldas',2)
hiel=surface_3d('./datasets\Capas Kale_Fm_Hiel.csv','#FFFF00','#FFFF00','Formación Hiel',2)
lluvia=surface_3d('./datasets\Capas Kale_Fm_Lluvi.csv','#FFFF00','#FFFF00','Formación Lluvia',2)
mugros=surface_3d('./datasets\Capas Kale_Fm_Mugros.csv','#FED99A','#FED99A','Formación Mugrosa',2)