from pydoc import classname
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
from plotly.subplots import make_subplots
import io
from flask import Flask
import os
from geoseismo import *
import warnings
from graficas.iny_bar_total import fig as iny_bar



warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None 

#Area del estudio
los=-73
loi=-74.4
lai=6.5
las=9

#Se cargan los datos de elevacion estos fueron descargados en https://portal.opentopography.org/datasets
# Global Bathymetry and Topography at 15 Arc Sec: SRTM15+ V2.1  
df_topo   =pd.read_csv('datasets/topo_src_15.xyz',delim_whitespace=True,header=None,decimal='.')
df_topo   =df_topo[(df_topo[1]>lai)&(df_topo[1]<las)&(df_topo[0]>loi)&(df_topo[0]<los)] #Filtros previos
mesh_topo = (df_topo.pivot(index=1, columns=0,values=2))
z_topo,x_topo,y_topo=mesh_topo.values,mesh_topo.columns,mesh_topo.index

topog=go.Surface(z=z_topo,showscale=False, x=x_topo, y=y_topo,colorscale=['black','black'],lighting=dict(ambient=0.3,diffuse=0.5),
                    showlegend=False,opacity=1,name='Topografía',hoverinfo='none')
#Base de datos de sismos convertidos a csv desde http://bdrsnc.sgc.gov.co/paginas1/catalogo/Consulta_Valle_Medio/valle_medio.php
df_sismos=pd.read_csv(r'datasets\reporte_LBG.csv')
df_sismos['FECHA - HORA UTC']=df_sismos['Fecha  (UTC)'].astype(str)+' '+df_sismos['Hora  (UTC)'].astype(str)
df_sismos.rename(columns = {'Latitud(°)':'LATITUD (°)', 
                                'Longitud(°)':'LONGITUD (°)',
                                'Profundidad(Km)':'PROF. (Km)',
                                'Magnitud':'MAGNITUD',
                                'Tipo Magnitud':'TIPO MAGNITUD',
                                'Rms(Seg)':'RMS (Seg)',
                                'Gap(°)':'GAP (°)',
                                'Error  Latitud(Km)':'ERROR LATITUD (Km)',
                                'Error  Longitud(Km)':'ERROR LONGITUD (Km)',
                                'Error  Profundidad(Km)':'ERROR PROFUNDIDAD (Km)'}, inplace = True)
df_sismos.drop(['Fecha  (UTC)','Hora  (UTC)'],axis=1,inplace=True)
df_sismos=df_sismos[(df_sismos['PROF. (Km)']<=32)&(df_sismos['PROF. (Km)']>(z_topo.min()*(-1/1000)))&(df_sismos['MAGNITUD']>0)& #Filtros previos
        (df_sismos['LATITUD (°)']>lai)&(df_sismos['LATITUD (°)']<las)
        &(df_sismos['LONGITUD (°)']>loi)&(df_sismos['LONGITUD (°)']<los)]
df_sismos['PROF. (m)']=-df_sismos['PROF. (Km)']*1000 #
df_sismos['ERROR PROFUNDIDAD (m)']=df_sismos['ERROR PROFUNDIDAD (Km)']*1000 #Conversion de km a m
df_sismos['ERROR LONGITUD (°)']=df_sismos['ERROR LONGITUD (Km)']/111.1 #Conversion de km a °
df_sismos['ERROR LATITUD (°)']=df_sismos['ERROR LATITUD (Km)']/111.1 
df_sismos['FECHA - HORA UTC']=pd.to_datetime(df_sismos['FECHA - HORA UTC'],infer_datetime_format=False)
# df_sismos['FECHA - HORA UTC'].apply(lambda x:pd.to_datetime(x))#Conversion de str a UTCDateTime

#Errores con topografia
df_sismos_err=df_sismos[df_sismos['PROF. (m)']+df_sismos['ERROR PROFUNDIDAD (m)']>(z_topo.min())]
df_sismos_no_err=df_sismos[df_sismos['PROF. (m)']+df_sismos['ERROR PROFUNDIDAD (m)']<=(z_topo.min())]
df_sismos_no_err.loc[:,'ERROR PROFUNDIDAD SUP (m)']=df_sismos_no_err.loc[:,'ERROR PROFUNDIDAD (m)'].copy()
z=[]
for x,y,zhip,zerr in zip(df_sismos_err['LONGITUD (°)'],df_sismos_err['LATITUD (°)'],
                df_sismos_err['PROF. (m)'],df_sismos_err['ERROR PROFUNDIDAD (m)']):
    df_elev=df_topo[(df_topo[0]<(x+0.005))&(df_topo[0]>(x-0.005))&
                (df_topo[1]<(y+0.005))&(df_topo[1]>(y-0.005))]
    d=1
    for x0,y0,z0 in zip(df_elev[0],df_elev[1],df_elev[2]):
        dist=np.sqrt(((x-x0)**2)+((y-y0)**2))
        if dist<d:
            d=dist
            z1=z0
    if z1<=(zhip+zerr):
        z.append(z1-zhip)
    else :
        z.append(zerr)
df_sismos_err.loc[:,'ERROR PROFUNDIDAD SUP (m)']=(np.array(z))
df_sismos=pd.concat([df_sismos_err, df_sismos_no_err])
del df_sismos_err
del df_sismos_no_err

#Inyeccion de H2O
iny=pd.read_csv(r'datasets\inyeccion_geo.csv',delimiter=';',decimal=',')
iny=iny[:-1]


inyec=[]
for name,lon,lat,alt in zip(iny['CAMPO'].astype("string"),iny['X'],iny['Y'],[2100]*len(iny['CAMPO'])):
    un=dict(
            showarrow=False,
            x=lon,
            y=lat,
            z=alt+10,
            text=name,
            xanchor="left",
            xshift=10,
            opacity=0.7,
            font=dict(
                color="black",
                size=12
            ))
    inyec.append(un)
del name,lon,lat,alt

#PPII
kalei,kicyl1,kibcircles1,kicyl2,kibcircles2,kicyl3,kibcircles3=vol_sus(-73.8566, 7.36551,3902,'Kalé - Investigación','blue',1651.9414772880211)
kaley,kycyl1,kybcircles1,kycyl2,kybcircles2,kycyl3,kybcircles3=vol_sus(-73.8571014, 7.3647799,2618.232,'Kalé - Inyector','aqua')
plai,picyl1,pibcircles1,picyl2,pibcircles2,picyl3,pibcircles3=vol_sus(-73.89389, 7.2572498,3227.8,'Platero - Investigación','red',1616.6333446235456)
play,pycyl1,pybcircles1,pycyl2,pybcircles2,pycyl3,pybcircles3=vol_sus(-73.8944016, 7.25667,2325.6,'Platero - Inyector','orange')

kalec,_,_,_,_,_,_=vol_sus(-73.8570023, 7.3647499,2325.6,'Kalé - Captador','orange')
plac,_,_,_,_,_,_=vol_sus(-73.8943024, 7.2566800,2325.6,'Platero - Captador','gold')

kale_tray=pd.read_csv('datasets\Kale-1H_1.csv')
kale_vert=go.Scatter3d(
    x=kale_tray[:51]['lon'], y=kale_tray[:51]['lat'], z=kale_tray[:51]['mt'],mode='lines',name='Kalé-Vertical',
    line=dict(
        color='red',
        width=5))
kale_hort=go.Scatter3d(
    x=kale_tray[51:]['lon'], y=kale_tray[51:]['lat'], z=kale_tray[51:]['mt'],mode='lines',name='Kalé-Horizontal',
    line=dict(
        color='darkblue',
        width=5))

kale_iny_tray=go.Scatter3d(
    x=[-73.8571014]*2, y=[7.3647799]*2, z=[69,-2618.232],mode='lines',name='Kalé - Inyector',
    line=dict(
        color='red',
        width=5))

kale_cap_tray=go.Scatter3d(
    x=[-73.8570023]*2, y=[7.3647499]*2, z=[69,-2325.6],mode='lines',name='Kalé - Captador',
    line=dict(
        color='red',
        width=5))

plat_tray=pd.read_csv('datasets\Platero-1H_1.csv')

plat_vert=go.Scatter3d(
    x=plat_tray[:36]['lon'], y=plat_tray[:36]['lat'], z=plat_tray[:36]['mt'],mode='lines',name='Platero-Vertical',
    line=dict(
        color='red',
        width=5))
plat_hort=go.Scatter3d(
    x=plat_tray[36:]['lon'], y=plat_tray[36:]['lat'], z=plat_tray[36:]['mt'],mode='lines',name='Platero-Horizontal',
    line=dict(
        color='darkblue',
        width=5))


plat_iny_tray=go.Scatter3d(
    x=[-73.8944016]*2, y=[7.25667]*2, z=[69,-2325.6],mode='lines',name='Platero - Inyector',
    line=dict(
        color='red',
        width=5))

plat_cap_tray=go.Scatter3d(
    x=[-73.8943024]*2, y=[7.2566800]*2, z=[69,-2325.6],mode='lines',name='Platero - Captador',
    line=dict(
        color='red',
        width=5))



#Estaciones sismologicas
df_sta_vmm=pd.read_csv('datasets/VMM_STA.csv',delimiter=';',decimal=',')
df_sta_lom=pd.read_csv('datasets//LOMA_STA.csv',delimiter=';',decimal=',')

STA_VMM = go.Scatter3d(
    x=df_sta_vmm['LONGITUD'],
    y=df_sta_vmm['LATITUD'],
    z=df_sta_vmm['ALTITUD (msnm)']+10, #Para sobresalir de la topografía
    mode='markers',
    marker_symbol='diamond',
    name="Estación sismologica VMM",
    hovertemplate ='Longitud:'+df_sta_vmm['LONGITUD'].astype(str)+'°'+'<br>'+
                    'Latitud:'+df_sta_vmm['LATITUD'].astype(str)+'°'+'<br>'+
                    'Elevacion:'+df_sta_vmm['ALTITUD (msnm)'].astype(str)+'msnm <br>'+
                    'Nombre de la estación:'+df_sta_vmm['NOMBRE ESTACIÓN']+'°'+'<br>'+
                    'Código:'+df_sta_vmm['CODIGO']+'<br>'+
                    'Agencia:'+df_sta_vmm['AGENCIA']+'<br>'+
                    'Fecha de instalación:'+df_sta_vmm['FECHA DE INSTALACIÓN'].astype(str)+'<br>'+
                    'Fecha de retiro:'+df_sta_vmm['FECHA DE RETIRO'].astype(str)+'<br>'+
                    'Estado:'+df_sta_vmm['ESTADO'],
    marker=dict(
        size=4,
        color='blueviolet'
    ),
    showlegend=False
)
STA_LOM = go.Scatter3d(
    x=df_sta_lom['LONGITUD'],
    y=df_sta_lom['LATITUD'],
    z=df_sta_lom['ALTITUD (msnm)']+10,
    mode='markers',
    marker_symbol='diamond',
    name="Estación sismologica la Loma, Cesar",
    hovertemplate ='Longitud:'+df_sta_lom['LONGITUD'].astype(str)+'°'+'<br>'+
                    'Latitud:'+df_sta_lom['LATITUD'].astype(str)+'°'+'<br>'+
                    'Elevacion:'+df_sta_lom['ALTITUD (msnm)'].astype(str)+'msnm <br>'+
                    'Nombre de la estación:'+df_sta_lom['NOMBRE ESTACIÓN']+'°'+'<br>'+
                    'Código:'+df_sta_lom['CODIGO']+'<br>'+
                    'Agencia:'+df_sta_lom['AGENCIA']+'<br>'+
                    'Fecha de instalación:'+df_sta_lom['FECHA DE INSTALACIÓN'].astype(str)+'<br>'+
                    'Fecha de retiro:'+df_sta_lom['FECHA DE RETIRO'].astype(str)+'<br>'+
                    'Estado:'+df_sta_lom['ESTADO'],
    marker=dict(
        size=6,
        color='blueviolet'
    ),
    showlegend=False
)
del df_sta_vmm,df_sta_lom

#Geologia superficial
df_geos=pd.read_csv('datasets/geo_unit_sup.csv')


#Rios
rivers=pd.read_csv('datasets/drenajes.csv')
rivers_ls=[]
for i in rivers['LINE_ID'].unique():
    riv1=rivers[rivers['LINE_ID']==i]
    rivers_ls.append(go.Scatter3d(x=riv1['X'], y=riv1['Y'], z=riv1['Z'],
                                    hovertemplate=str(np.array(riv1['NOMBRE_GEO'])[0]),
                                    mode='lines',
                                    name='Ríos',line=dict(color='aqua',width=4),showlegend=False))
del rivers,i

#Cargar datos de pozos
df_pozos=pd.read_csv('datasets/pozos.csv',usecols=['lon', 'lat', 'UWI', 'WELL_NAME', 
'DEPARTAMEN', 'WELL_COU_1', 'WELL_TVD', 'WELL_KB_EL',
       'ROTARY_ELE', 'WELL_DRILL', 'WELL_GROUN', 'FIELD_ABRE',
       'CONTRATO', 'WELL_SPUD_', 'COORD_QUAL', 'COMMENT_', 'WELL_COMPL', 'WELL_STA_1',
       'WELLTYPE', 'FECHA_ACTU',
       'OPERATOR_W', 'COMPANY_CO', 'z'])
Pozos = go.Scatter3d(
    x=df_pozos['lon'],
    y=df_pozos['lat'],
    z=df_pozos['z']+15,
    mode='markers',
    name="Pozo petrolífero",
    hovertemplate ='Longitud:'+df_pozos['lon'].astype(str)+'°'+'<br>'+
                    'Latitud:'+df_pozos['lat'].astype(str)+'°'+'<br>'+
                    'Elevacion:'+df_pozos['z'].astype(str)+'msnm <br>'+
                    'UWI:'+df_pozos['UWI']+'°'+'<br>'+
                    'Nombre del pozo:'+df_pozos['WELL_NAME']+'<br>'+
                    'Departamento:'+df_pozos['DEPARTAMEN']+'<br>'+
                    'Municipio:'+df_pozos['WELL_COU_1']+'<br>'+
                    'Tipo:'+df_pozos['WELLTYPE']+'<br>'+
                    'Operador:'+df_pozos['OPERATOR_W']+'<br>'+
                    'Compañia:'+df_pozos['COMPANY_CO'],
    error_z=dict(
    array=[0]*len(df_pozos['WELL_TVD']), 
    arrayminus=df_pozos['WELL_TVD'].values*0.3048 ,             
    color='black',   # choose a colorscale
    symmetric=False,
    width=0.01,
    visible=True),
    marker=dict(
        size=1.5,
        color='black'
    )
)

# pozos_ls=[]
# conteo=0
# for i in df_pozos['WELL_NAME']:
#     if conteo<350:
#         pozos_1=df_pozos[df_pozos['WELL_NAME']==i]
#         prof=pozos_1['WELL_TVD'].values[0]*0.3048
#         pozos_2=go.Scatter3d(x=[pozos_1['lon'].values[0]]*2,
#                                         y=[pozos_1['lat'].values[0]]*2,
#                                         z=[pozos_1['z'].values[0],prof*-1],
#                         name=i,
#                         mode='lines',
#                         line=dict(
#                             color='black',
#                             width=5),
#                         showlegend=False)
#         pozos_ls.append(pozos_2)
#         conteo=conteo+1
#     else:
#         pass

del df_pozos
#Integridad Pozos Kale
critic=pd.read_csv('datasets/criticidad_Kale.csv',decimal=',')

critic['color']=critic['Integridad'].apply(lambda x:Color_Integridad(x))
criticidad=go.Scatter3d(x=critic['lon'],y=critic['lat'],z=[69+100]*len(critic['X']),
                        name='Integridad Pozos Kale',
                        mode='markers',
                        marker_symbol='diamond',
                        hovertemplate='Pozo:'+critic['WELL_NAME'].astype(str)+'<br>Valoración:'+
                                        critic['Valoracion'].astype(str)+'<br>Condición:'+
                                        critic['Integridad'].astype(str)+'<br>Estado:'+
                                        critic['Estado del Pozo'].astype(str),
                        marker=dict(
                                    size=6,
                                    color=critic['color'],               
                                    opacity=1,
                                ))

well_criticidad=[]
for i in critic['WELL_NAME']:
    critic_1=critic[critic['WELL_NAME']==i]
    TVD=critic_1['WELL_TVD'].values[0]*0.3048
    if TVD<1:
        pass
    else:
        well_criticidad_1=go.Scatter3d(x=[critic_1['lon'].values[0]]*2,
                                     y=[critic_1['lat'].values[0]]*2,
                                     z=[0,TVD*-1],
                        name=i,
                        mode='lines',
                        line=dict(
                            color='red',
                            width=5),
                        showlegend=False)
        well_criticidad.append(well_criticidad_1)

del critic,i

#Rezumaderos
df_rezumaderos=pd.read_csv('datasets\REZUMADEROS_WGS84_SIM.txt',decimal=',',delimiter=';')
rez_txt=('Longitud:'+df_rezumaderos['X'].astype(str)+'°'+
            '<br>'+'Latitud:'+df_rezumaderos['Y'].astype(str)+'°'+
            '<br>'+'Elevacion:'+df_rezumaderos['Z'].astype(str)+'msnm'+
            '<br>'+'Tipo:'+df_rezumaderos['TIPO'].astype(str)+
            '<br>'+'Autor:'+df_rezumaderos['AUTOR'].astype(str)+
            '<br>'+'Empresa:'+df_rezumaderos['EMPRESA'].astype(str)+
            '<br>'+'Formación:'+df_rezumaderos['FORMACION_'].astype(str)+
            '<br>'+'Tipo secundario:'+df_rezumaderos['TIPO_2'].astype(str)+
            '<br>'+'Departamento:'+df_rezumaderos['DPTOS_NOMB'].astype(str)+
            '<br>'+'Capital:'+df_rezumaderos['CAPITAL'].astype(str))
rez = go.Scatter3d(
    x=df_rezumaderos['X'],
    y=df_rezumaderos['Y'],
    z=df_rezumaderos['Z'],
    mode='markers',
    name="Rezumaderos",
    hovertemplate =rez_txt,
    marker=dict(
        size=5,
        color='gray'
    ),
    showlegend=False
)

del df_rezumaderos,rez_txt

#Tope Pozos Olini
ol=pd.read_csv('datasets/topes_olini.csv')
ol_ls=[]
for i in ol.index:
    ol_1=ol[ol.index==i]
    # print([ol_1['Depth [X Absolute]'].values[0]]*2)
    # print([ol_1['Depth [Y Absolute]'].values[0]]*2)
    ol_ls.append(go.Scatter3d(x=[ol_1['lon'].values[0]]*2, 
                              y=[ol_1['lat'].values[0]]*2, 
                              z=[ol_1['top_Depth (mt)'].values[0]*-1,ol_1['Depth (mt)'].values[0]*-1],
                                    hovertemplate=ol_1['TOPE FM'].values[0],
                                    mode='lines',
                                    name=ol_1['POZO'].values[0],
                                    line=dict(color=[ol_1['colors'].values[0]]*2,width=4),showlegend=False))

del ol,i

#Stress map
stress=pd.read_csv('datasets/wsm2016.csv',delimiter=',',decimal='.')
st=stress[
    (stress['LAT']>=6.5)&
    (stress['LAT']<=9)&
    (stress['LON']>=-74.4)&
    (stress['LON']<=-73)
]

st_ls=[]
for i in st.index:
    st_1=st[st.index==i]
    x=st_1['LON'].values[0]
    y=st_1['LAT'].values[0]
    xx = st_1['LON'].values[0] + (0.2 * np.cos(np.radians(az2pyt(st_1['AZI'].values[0]))))
    yy = st_1['LAT'].values[0] + (0.2 * np.sin(np.radians(az2pyt(st_1['AZI'].values[0]))))
    text=''
    for i in ['TYPE','DEPTH','QUALITY','REGIME','LOCALITY','S1AZ','S1PL', 'S2AZ', 'S2PL', 'S3AZ', 'S3PL','REF1','COMMENT']:
        text=text+str(i)+':'+str(st_1[i].values[0])+'<br>'
    st_ls.append(go.Cone(
        x=[xx],
        y=[yy],
        z=[8000],
        u=[0.3*(xx-x)],
        v=[0.3*(yy-y)],
        w=[0],
        sizemode="absolute",
        sizeref=0.1,
        colorscale=[[0, "black"], [1, "black"]],
        anchor="tip",
        hovertemplate=text,
        name=st_1['ID'].values[0],
        showscale= False))

del stress,i,st

#Poblaciones
df_poblaciones=pd.read_csv('datasets/poblaciones.csv',usecols=['Name','lon','lat','outputSRTM1'])
Poblaciones = go.Scatter3d(
    x=df_poblaciones['lon'],
    y=df_poblaciones['lat'],
    z=df_poblaciones['outputSRTM1']+10, #Conseguir alturas
    mode='markers+text',
    text=df_poblaciones['Name'],
    textposition= 'top center',
        textfont=dict(
        family="Poppins",
        size=12,
        color="black"
    ),
    name="Población",
    marker_symbol='square',
    #hovertemplate =df_poblaciones['Name'],
    marker=dict(
        size=6,
        color='red'
    ),
    # textposition="bottom right"
)
# Pobl=[]
# for name,lon,lat,alt in zip(df_poblaciones['Name'],df_poblaciones['lon'],
# df_poblaciones['lat'],df_poblaciones['outputSRTM1']):
#     un=dict(
#             showarrow=False,
#             x=lon,
#             y=lat,
#             z=alt+10,
#             text=name,
#             xanchor="left",
#             xshift=10,
#             opacity=0.7,
#             font=dict(
#                 color="black",
#                 size=12
#             ))
#     Pobl.append(un)

del df_poblaciones,un

#Carreteras
roads=pd.read_csv('datasets\Via_WGS84_SIM.txt',delimiter=';',decimal=',')
roads  =roads[(roads['LATITUD']>lai)&(roads['LATITUD']<las)&(roads['LONGITUD']>loi)&(roads['LONGITUD']<los)]
roads_ls=[]
for i in roads['GLOBALID'].unique():
    f=roads[roads['GLOBALID']==i]
    roads_ls.append(go.Scatter3d(x=f['LONGITUD'], y=f['LATITUD'], z=f['ELEVACION'],
    hovertemplate=str(i),mode='lines',name='Via',line=dict(color='yellow',width=2),showlegend=False),)

del roads,i

#Fallas
fallas=pd.read_csv('datasets/fallas_SIM.csv',decimal=',')
fallas['X']=fallas['X'].astype(float)
fallas['Y']=fallas['Y'].astype(float)
fallas['Z']=fallas['Z'].astype(float)
fallas_1=pd.read_csv('datasets/fallas_1_SIM.csv')
fallas_1=fallas_1.drop_duplicates(subset=['LINE_ID'])

fallas_ls=[]
for i in fallas['LINE_ID'].unique():
    f=fallas[fallas['LINE_ID']==i]
    attr=fallas_1[fallas_1['LINE_ID']==i]
    try:
        nom=np.array(attr['NombreFall'])[0]
    except:
        nom='_'
    try:
        tip=np.array(attr['Tipo'])[0]
    except:
        tip='_'
    fallas_ls.append(go.Scatter3d(x=f['X'], y=f['Y'], z=f['Z'],
                    hovertemplate=nom,
                    mode='lines',
                    name=tip,line=dict(color='red',width=4),showlegend=False),)
del fallas,fallas_1,i
#Campos
campet=pd.read_csv('datasets\campos_SIM.csv',decimal=',')
campet['X']=campet['X'].astype(float)
campet['Y']=campet['Y'].astype(float)
campet['Z']=campet['Z'].astype(float)
campet_1=pd.read_csv('datasets/campos_1_SIM.csv')
campet_1=campet_1.drop_duplicates(subset=['LINE_ID'])

campet_ls=[]
for i in campet['LINE_ID'].unique():
    f=campet[campet['LINE_ID']==i]
    attr=campet_1[campet_1['LINE_ID']==i]
    nom='Compañia:'+np.array(attr['Compañia'])[0]+'<br>Estado:'+np.array(attr['Estado'])[0]+'<br>Información:'+str(np.array(attr['INFO'])[0])
    try:
        tip='Campo petrolífero '+np.array(attr['Campo'])[0]
    except:
        tip='_'
    campet_ls.append(go.Scatter3d(x=f['X'], y=f['Y'], z=f['Z'],
                    hovertemplate=nom,
                    mode='lines',
                    name=tip,line=dict(color='black',width=3),showlegend=False),)

del campet,campet_1,i
#Superficies geológicas

Eoceno=surface_3d('datasets/DISCORDANCIA_EOCENO.txt','#FDA75F','#9d4702','Discordancia del Eoceno Medio',1)
Colorado=surface_3d('datasets/TOPE_COLORADO.txt','#FEC07A','#d06f01','Tope Formación Colorado',1)
Mugrosa=surface_3d('datasets/TOPE_MUGROSA.txt','#ffa46b','#b34400','Tope Formación Mugrosa',1)
Chorros=surface_3d('datasets/TOPE_CHORROS.txt','#FDB46C','#974d02','Tope Grupo Chorros',1)
Real=surface_3d('datasets/BASE_CUATERNARIO.txt','#FFFF00','#adad00','Tope Grupo Real',1)

paja=surface_3d('datasets/PAJA_SGC_TVDSS_3.xyz','#8CCD57','#8CCD57','Formación Paja',2)
salada=surface_3d('datasets/SALADA_SGC_TVDSS_3.xyz','#BFE35D','#BFE35D','Formación Salada',2)
simiti=surface_3d('datasets/SIMITI_SGC_TVDSS_3.xyz','#BFE48A','#BFE48A','Formación Simiti',2)
galembo=surface_3d('datasets/GALEMBO_SGC_TVDSS_3.xyz','#E6F47F','#E6F47F','Formación Galembo',2)

ciraShale=surface_3d('datasets\Capas Kale_Base_CiraShale.csv','#FFE619','#FFE619','Cira Shale',2)
bagre=surface_3d('datasets\Capas Kale_Fm_Bagre.csv','#FFFF00','#FFFF00','Formación Bagre',2)
chontorales=surface_3d('datasets\Capas Kale_Fm_Chontorales.csv','#FFFF00','#FFFF00','Formación Chontorales',2)
colorado=surface_3d('datasets\Capas Kale_Fm_Colorado.csv','#FEE6AA','#FEE6AA','Formación Colorado',2)
enrejado=surface_3d('datasets\Capas Kale_Fm_Enrejado.csv','#FFFF00','#FFFF00','Formación Enrejado',2)
esmeraldas=surface_3d('datasets\Capas Kale_Fm_Esmeraldas.csv','#FDCDA1','#FDCDA1','Formación Esmeraldas',2)
hiel=surface_3d('datasets\Capas Kale_Fm_Hiel.csv','#FFFF00','#FFFF00','Formación Hiel',2)
lluvia=surface_3d('datasets\Capas Kale_Fm_Lluvi.csv','#FFFF00','#FFFF00','Formación Lluvia',2)
mugros=surface_3d('datasets\Capas Kale_Fm_Mugros.csv','#FED99A','#FED99A','Formación Mugrosa',2)

#Colores geologia
df_colors_geo=pd.read_csv('datasets/UN_CRN_COLORS.csv',index_col=None)

#Sismica
sismica_1=img_3d("ANH-TR-2006-04-A","assets\ANH-TR-2006-04A.jpg",
                 -74.076876,7.560287,-72.959474,6.809403,1726.31231739848,-7030.775458)

sismica_2=img_3d("CP-2010-1032","assets\CP-2010-1032.jpg",
                 -73.73048,7.68415,-73.50918,7.52588,295.6063016,-10267.22761)

sismica_3=img_3d("CP-2008-1385","assets\CP-2008-1385.jpg",
                 -73.69137,7.45833,-73.47157,7.77188,268.4709044,-9351.70593)

sismica_4=img_3d("CP-2008-1190","assets\CP-2008-1190.jpg",
                 -73.87223,7.37559,-73.5522,7.77086,281.2813151,-9394.211046)

#Hidrogeología
hidro_well=pd.read_csv('datasets\inv_hidro.csv')
hidrogeo=go.Scatter3d(
    x=hidro_well['LONGITUD'],
    y=hidro_well['LATITUD'],
    z=np.array(hidro_well['Z_PTO'])+100, #Para sobresalir de la topografía
    mode='markers',
    name='Inventario de puntos de agua',
    hovertemplate =hidro_well['T_PUNTO']
                    +'<br>CODIGO SGC: '+hidro_well['COD_SGC']
                    +'<br>Departamento: '+hidro_well['DEPTO_LOC']
                    +'<br>Municipio: '+hidro_well['MUN_LOC']
                    +'<br>Vereda: '+hidro_well['VER_LOC']
                    +'<br>Sitio: '+hidro_well['SITIO_LOC']
                    +'<br>Unidad Geológica: '+hidro_well['U_GEOL']
                    +'<br>COND_SECO: '+hidro_well['COND_SECO'].astype(str)
                    +'<br>COND_HUM: '+hidro_well['COND_HUM'].astype(str)
                    ,
    marker=dict(
        size=2,
        color='darkblue'
    ),
    showlegend=False
)
del hidro_well
#Pozos en prof hidrogeo
hw=pd.read_csv('datasets/pozos_adquisicion_hidro.csv')

hidro_wells=go.Scatter3d(x=hw['lon'],y=hw['lat'],z=[69]*len(hw['lon']),
                        name='Pozos de agua subterránea',
                        mode='markers',
                        marker_symbol='diamond',
                        hovertemplate='Pozo:'+hw['NOMBRE'].astype(str)+'<br>CONSECUTIVO:'+
                                              hw['CONSECUTIVO'].astype(str)+'<br>pH:'+
                                              hw['pH'].astype(str)+'<br>CE(µS/cm):'+
                                              hw['CE(µS/cm)'].astype(str)+'<br>Ca(mg/L):'+
                                              hw['Ca(mg/L)'].astype(str)+'<br>HCO3(mg/L):'+
                                              hw['HCO3(mg/L)'].astype(str)+'<br>Prof(m):'+
                                              hw['Prof(m)'].astype(str)
                                        ,
                        marker=dict(
                                    size=2,
                                    color='blue',               
                                    opacity=1,
                                ))

hw_ls=[]
for i in hw['NOMBRE']:
    hw_1=hw[hw['NOMBRE']==i]
    prof=hw_1['Prof(m)'].values[0]
    hw_2=go.Scatter3d(x=[hw_1['lon'].values[0]]*2,
                                    y=[hw_1['lat'].values[0]]*2,
                                    z=[69,prof*-1],
                    name=i,
                    mode='lines',
                    line=dict(
                        color='aqua',
                        width=10),
                    showlegend=False)
    hw_ls.append(hw_2)

del hw,i

#Explicacion modelo
exp=io.open("datasets\Explicacion_modelo3d.txt", mode="r", encoding="utf-8")
ls_k=[html.H2('¿Cómo funciona el modelo tridimensional del Valle Medio del Magdalena?', className="card-text")]
for i in exp:
    ls_k.append(html.H6(i, className="card-text"))

#Fallas geologicas 3d
fs=pd.read_csv('datasets/new_surfaces.txt')

g1,g2,g3=[],[],[]
for n,ls in zip(fs['clas'].unique(),[g1,g2,g3]):
        fs1=fs[fs['clas']==n]
        for i in fs1['name'].unique():
            fs2=fs1[fs['name']==i]
            fs2=fs2.drop_duplicates()
            mesh_geo=fs2.pivot(index='Y', columns='X',values='Z')
            fault_surface=go.Surface(z=mesh_geo.values*-1,showscale=False, x=mesh_geo.columns, 
                    y=mesh_geo.index,showlegend=False,opacity=0.9,colorscale=['red','pink'],hovertemplate=i,name='Falla geológica')
            ls.append(fault_surface)
del n,ls,fs

server = Flask(__name__)
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP],
                server=server,
                meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],)
app.config['suppress_callback_exceptions'] = True
#Cargar los datos

card_main=html.Div(
        
            [
            html.H4('Visualización:'),
            html.Div([
            html.Div([html.H5("Transparencia:", className="helps1 column"), 
                      html.A(
                          html.H5("?"),
                          id='tTrans',
                          className="column helps2")
                      ],
            className='row flex-display'),
            dbc.Tooltip(
            "Usa la barra deslizadora para seleccionar diferentes niveles de transparencia de las superficies tridimensionales desplegadas. 0 = Transparencia total. 1 = Sin transparencia. Para desactivar la topografía selección un valor de 0.",
            target='tTrans',
            ),
            html.H6("Topografía:", className="card-subtitle",style= {"margin-top": "10px","margin-left":"15px"}),
            dcc.Slider(
                id='TOPO',
                min=0,
                max=1,
                step=0.1,
                value=0.9,
                tooltip={"placement": "bottom", "always_visible": False},),
                #Condicionales de geologia-Tope Grupo real
                html.Div(id='GREAL', children=[
                        html.H6("Tope Grupo Real:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TGREAL',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Tope Grupo real
                html.Div(id='COLORADO', children=[
                        html.H6("Tope Formación Colorado:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TCOLORADO',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Tope Fm Mugrosa
                html.Div(id='MUGROSA', children=[
                        html.H6("Tope Formación Mugrosa:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TMUGROSA',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Tope Grupo real
                html.Div(id='CHORROS', children=[
                        html.H6("Tope Formación Chorros:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TCHORROS',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Tope Grupo real
                html.Div(id='EOCMED', children=[
                        html.H6("Discordancia del Eoceno Medio:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TEOCMED',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Fm Paja
                html.Div(id='PAJA', children=[
                        html.H6("Formación Paja:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TPAJA',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Fm Salada
                html.Div(id='SALADA', children=[
                        html.H6("Formación Salada:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TSALADA',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Fm Simiti
                html.Div(id='SIMITI', children=[
                        html.H6("Formación Simiti:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TSIMITI',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
                #Condicionales de geologia-Fm Galembo
                html.Div(id='GALEMBO', children=[
                        html.H6("Formación Galembo:", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TGALEMBO',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Cira Shale
                html.Div(id='CIRASHALE', children=[
                        html.H6("Cira Shale (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TCIRASHALE',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Bagre
                html.Div(id='BAGRE', children=[
                        html.H6("Formación Bagre (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TBAGRE',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Chontorales
                html.Div(id='CHONTORALES', children=[
                        html.H6("Formación Chontorales (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TCHONTORALES',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Colorado
                html.Div(id='COLORADOH', children=[
                        html.H6("Formación Colorado (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TCOLORADOH',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Enrejado
                html.Div(id='ENREJADO', children=[
                        html.H6("Formación Enrejado (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TENREJADO',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Esmeraldas
                html.Div(id='ESMERALDAS', children=[
                        html.H6("Formación Esmeraldas (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TESMERALDAS',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Hiel
                html.Div(id='HIEL', children=[
                        html.H6("Formación Hiel (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='THIEL',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Lluvia
                html.Div(id='LLUVIA', children=[
                        html.H6("Formación Lluvia (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TLLUVIA',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
		#Mugrosa
                html.Div(id='MUGROSAH', children=[
                        html.H6("Formación Mugrosa (ECP):", className="card-subtitle",style={"margin-left":"15px"}),
                        # Create element to hide/show, in this case a slider
                        dcc.Slider(id='TMUGROSAH',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                tooltip={"placement": "bottom", "always_visible": False})

                    ], style= {'display': 'none',"margin-top": "10px",'marginLeft':'12px'}),
           #Fin condicionales
            html.Div([html.H5("Exageración vertical:", className="helps1 column"),
                      
                      html.A(children=html.H5("?"),
                             id='tExg',
                             className="column helps2"
                             )
                      ],
                     className='row flex-display'),
            #html.H5("Exageración vertical:", className="card-subtitle",id='tExg',style= {"margin-top": "10px"}),
            dbc.Tooltip(
            "Selecciona diferentes niveles de exageración vertical para aumentar o disminuir la escala vertical de la gráfica 3D con respecto a la escala horizontal. ",
            target="tExg",
            ),
            dcc.Slider(
                id='EXG',
                min=1,
                max=10,
                step=1,
                value=2,
                tooltip={"placement": "bottom", "always_visible": False}),
                html.Div([html.H5("Perfil:", className="helps1 column"),
                          html.A(children=html.H5("?"),    
                                 id='tPerfil',
                                 className="column helps2"
                                 )
                          ],
                         className='row flex-display',style={'marginBottom': 5, 'marginTop': 10}), 
                #Perfil
                dbc.Tooltip(
                "Puedes crear un perfil que se despliega en la parte inferior de la gráfica 3D, para visualizar diferentes datos seleccionados dentro de un margen de distancia o buffer de 0.1° (~11 km). Selecciona las coordenadas en latitud y longitud del punto inicial y punto final.",
                target="tPerfil",
                ),
                html.Div([
                html.H6("Punto Inicial (Longitud-Latitud)", className="card-subtitle",style= {"margin-top": "10px",'font-size':'1.8rem'}),
                html.Div([dcc.Input(id="Longitud 1", type="number", placeholder="Longitud 1", min=loi, max=los, step=0.01,style={'marginRight':'10px'},value=loi),
                dcc.Input(id="Latitud 1", type="number", placeholder="Latitud 1", min=lai, max=las, step=0.01, debounce=True,value=lai)],style={'font-size': '12px'}),
                html.H6("Punto Final (Longitud-Latitud)", className="card-subtitle",style= {"margin-top": "10px",'font-size':'1.8rem'}),
                html.Div([dcc.Input(id="Longitud 2", type="number", placeholder="Longitud 2", min=loi, max=los, step=0.01,value=los,style={'marginRight':'10px'}),
                dcc.Input(id="Latitud 2", type="number", placeholder="Latitud 2", min=lai, max=las, step=0.01,value=las,debounce=True)],style={'font-size': '12px'})],style={'marginLeft': '12px'})],
                style={'marginLeft':'10px'}),
            html.Div([html.H4("Cartografía base:", className="helps1 column"),
                      html.A(children=html.H5("?"),    
                             id='tCart',
                             className="column helps2"
                             )
                      ],
                     className='row flex-display',style={'marginBottom': 1, 'marginTop': 10}),                
            #html.H5("Cartografía base:",id='tCart', className="card-subtitle",style= {"margin-top": "10px"}),
            dbc.Tooltip(
            "Selecciona diferentes capas de datos para referencia de ubicación básica en el territorio.",
            target="tCart",
            ),
            html.Div(children=[dcc.Dropdown(id='CART',
                        placeholder="Variables a desplegar...",
                        style={'color': 'black'},
                        options=[
                            {'label': ' Estaciones sismológicas (SGC)', 'value': 'STA'},
                            {'label': ' Poblaciones (UNAL-ANH-MINCIENCIAS)', 'value': 'POB'},
                            {'label': ' Drenajes (IGAC)', 'value': 'RIV'},
                            {'label': ' Vias (IGAC)*', 'value': 'VIA'},
                            {'label': ' Perfil', 'value': 'PER'},
                            
                        ],
                        value=[],
                        multi=True)],style={'font-size': '12px'}),
            html.H4('Sismicidad:'),
            html.Div([
            html.Div([html.H5("Magnitudes:", className="helps1 column"),
                      html.A(children=html.H5("?"),    
                                 id='tMag',
                                 className="column helps2"
                                 )
                      ],
                     className='row flex-display'),
            #html.Div(id='mag_div', children=[html.H5("Magnitudes:", className="card-subtitle",id='tMag'),
            dbc.Tooltip(
            "Filtra los sismos desplegados en la gráfica 3D a partir de sus magnitudes. Puedes mover los círculos de cada extremo de la barra deslizadora para restringir el rango de las magnitudes.",
            target="tMag",
            ),
            html.Div([dcc.RangeSlider(
                id='MAGN',
                min=df_sismos['MAGNITUD'].min(),
                max=df_sismos['MAGNITUD'].max(),
                step=0.1,
                value=[df_sismos['MAGNITUD'].min(), df_sismos['MAGNITUD'].max()],
                marks={
                        0: {'label':' 0 M', 'style': {'color': 'white'}},
                        1: {'label':'1 M', 'style': {'color': 'white'}},
                        2: {'label':'2 M', 'style': {'color': 'white'}},
                        3: {'label':'3 M', 'style': {'color': 'white'}},
                        4: {'label':'4 M', 'style': {'color': 'white'}},
                        5: {'label':'5 M', 'style': {'color': 'white'}}},
                allowCross=False,
                tooltip={"placement": "bottom", "always_visible": False}
            )],style={'marginBottom': 30, 'marginTop': 10}),
            html.Div([html.H5("Profundidad:", className="helps1 column"),
                      html.A(children=html.H5("?"), 
                             id='tDep',
                             className="column helps2"
                             )
                      ],
                     className='row flex-display',style={'marginBottom': 1, 'marginTop': 20}),            
            #html.Div(id='dep_div', children=[html.H5("Profundidad (m):", className="card-subtitle",id='tDep'),
            html.Div([dbc.Tooltip(
            "Filtra los sismos desplegados en la gráfica 3D a partir de sus profundidades. Puedes mover los círculos de cada extremo de la barra deslizadora para restringir el rango de profundidad. La unidad de profundidad es m = metros.",
            target="tDep",
            ),
            dcc.RangeSlider(
                id='DEPTH',
                min=np.abs(df_sismos['PROF. (m)'].max()),
                max=np.abs(df_sismos['PROF. (m)'].min()),
                step=100,
                value=[np.abs(df_sismos['PROF. (m)'].max()),np.abs(df_sismos['PROF. (m)'].min())],
                marks={
                        0: {'label':'0 m', 'style': {'color': 'white'}},
                        8000: {'label':'8000 m', 'style': {'color': 'white'}},
                        16000: {'label':'16000 m', 'style': {'color': 'white'}},
                        24000: {'label':'24000 m', 'style': {'color': 'white'}},
                        32000: {'label': '32000 m', 'style': {'color': 'white'}}},
                allowCross=False,
                tooltip={"placement": "bottom", "always_visible": False}
            )],style={'marginBottom': 40, 'marginTop': 9}),
            html.Div([html.H5("Fecha:", className="helps1 column"),
                      html.A(children=html.H5("?"), 
                             id='tFecha',
                             className="column helps2"
                             )
                      ],
                     className='row flex-display',style={'marginBottom': 5, 'marginTop': 20}), 
            #html.H5("Fecha:",id='tFecha', className="card-subtitle",style= {"margin-top": "10px"}),
            dbc.Tooltip(
            "Selecciona la fecha inicial y fecha final del registro de sismos que quieres desplegar.",
            target="tFecha",
            ),
            html.Div(dcc.DatePickerRange(
                    id='DATE',
                    start_date_placeholder_text="Start Date",
                    end_date_placeholder_text="End Date",
                    calendar_orientation='horizontal',
                    start_date=df_sismos['FECHA - HORA UTC'].min(),
                    end_date=df_sismos['FECHA - HORA UTC'].max(),
                    day_size=30,
                    min_date_allowed=df_sismos['FECHA - HORA UTC'].min(),
                    max_date_allowed=df_sismos['FECHA - HORA UTC'].max(),
                    # with_portal=True,
                    persistence=True,
                    #initial_visible_month=df_sismos['FECHA - HORA UTC'].min(),
                    reopen_calendar_on_clear=False
                ),style={'font-size': '12px'}),
            html.Div([html.H5("Variables (SGC):", className="helps1 column"),
                      html.A(children=html.H5("?"), 
                             id='tSeis',
                             className="column helps2"
                             )
                      ],
                     className='row flex-display',style={'marginBottom': 1, 'marginTop': 10}),             
            #html.H5("Variables de sismicidad desplegadas (SGC):",id='tSeis', className="card-subtitle",style= {"margin-top": "10px"}),
            dbc.Tooltip(
            "Selecciona las diferentes variables de los datos de sismicidad del Servicio Geológico Colombiano (SGC) que quieres desplegar. Puedes también elegir si mostrar o no la sismicidad en la gráfica 3D.",
            target="tSeis",
            ),
            html.Div( children=[dcc.Dropdown(id='SEISMO',
                        placeholder="Variables a desplegar...",
                        style={'color': 'black'},
                        options=[
                            {'label': 'Localización', 'value': 'LOC'},
                            {'label': 'Fecha', 'value': 'FEC'},
                            {'label': 'Magnitud', 'value': 'MAG'},
                            {'label': 'RMS', 'value': 'RMS'},
                            {'label': 'Errores', 'value': 'ERR'},
                            {'label': ' Barras de Error ', 'value': 'ERROR'},
                            {'label': 'Mostrar sismicidad', 'value': 'SISM'}
                        ],
                        value=['LOC', 'FEC','MAG','RMS','ERR','SISM'],
                        multi=True,
                    )],style={'font-size': '12px',})],style={'marginLeft':'10px'}),
#----------------------------------
            #html.H5("_______________________", className="card-subtitle"),
            html.Div([html.H4("Geología:", className="helps1 column"),
                      html.A(children=html.H5("?"),                                
                             id='tGeo',
                             className="column helps2"
                             )
                      ],
                     className='row flex-display',style={'marginBottom': 1, 'marginTop': 10}),  
            #html.H5("Geología:",id='tGeo', className="card-subtitle",style= {"margin-top": "10px"}),
            dbc.Tooltip(
            "Selecciona capas de datos relacionados con la geología de superficie y del subsuelo.",
            target="tGeo",
            ),            
            html.Div(children=[dcc.Dropdown(id='GEOL',
                        placeholder="Variables a desplegar...",
                        style={'color': 'black'},
                        options=[
                            {'label': ' Fallas Geológicas (SGC)*', 'value': 'FALL'},
                            {'label': ' Tope Grupo Real (UNAL-ANH-MINCIENCIAS)', 'value': 'REAL'},
                            {'label': ' Tope Formación Colorado (UNAL-ANH-MINCIENCIAS)', 'value': 'COL'},
                            {'label': ' Tope Formación Mugrosa (UNAL-ANH-MINCIENCIAS)', 'value': 'MUG'},
                            {'label': ' Tope Grupo Chorros (UNAL-ANH-MINCIENCIAS)', 'value': 'CHO'},
                            {'label': ' Discordancia del Eoceno Medio (UNAL-ANH-MINCIENCIAS)', 'value': 'EOC'},
                            {'label': ' Formación Paja (ANH)', 'value': 'PAJA'},
                            {'label': ' Formación Salada (ANH)', 'value': 'SALADA'},
                            {'label': ' Formación Simiti (ANH)', 'value': 'SIMITI'},
                            {'label': ' Formación Galembo (ANH)', 'value': 'GALEMBO'},
                            {'label': ' Cira Shale (ECP)', 'value': 'CIRASHALE'},
                            {'label': ' Formación Bagre (ECP)', 'value': 'BAGRE'},
                            {'label': ' Formación Chontorales (ECP)', 'value': 'CHONTORALES'},
                            {'label': ' Formación Colorado (ECP)', 'value': 'COLORADOH'},
                            {'label': ' Formación Enrejado (ECP)', 'value': 'ENREJADO'},
                            {'label': ' Formación Esmeraldas (ECP)', 'value': 'ESMERALDAS'},
                            {'label': ' Formación Hiel (ECP)', 'value': 'HIEL'},
                            {'label': ' Formación Lluvia (ECP)', 'value': 'LLUVIA'},
                            {'label': ' Formación Mugrosa (ECP)', 'value': 'MUGROSAH'},                                                        
                            {'label': ' Geología superficial (SGC)', 'value': 'GEO'},
                            {'label': 'Superficies de fallas principales*', 'value': 'g1'},
                            {'label': 'Superficies de fallas (1-100)*', 'value': 'g2'},
                            {'label': 'Superficies de fallas (A-K)*', 'value': 'g3'}  
                        ],
                        value=[],
                        multi=True)],style={'font-size': '12px'}),
            #html.H5("_______________________", className="card-subtitle"),
            html.Div([html.H4("PPII:", className="helps1 column"),
                      html.A(children=html.H5("?"), 
                             id='tPPII',
                             className="column helps2"
                             )
                      ],
                     className='row flex-display',style={'marginBottom': 1, 'marginTop': 10}),                   
            #html.H5("PPII:", id='tPPII',className="card-subtitle",style= {"margin-top": "10px"}),
            dbc.Tooltip(
            "Selecciona los pozos de los Proyecto Piloto de Investigación Integral (PPII) que quieres desplegar. A su vez, puedes seleccionar los correspondientes volúmenes cilíndricos de monitoreo del semáforo sísmico para los pozos de investigación e inyector.",
            target="tPPII",
            ),
            html.Div(children=[dcc.Dropdown(id='PPII',
                        placeholder="Variables a desplegar...",
                        style={'color': 'black'},
                        options=[
                            {'label': ' Pozo Kalé - Investigación (ANH)', 'value': 'KALEi'},
                            {'label': ' Volúmenes de Monitoreo Kalé - Investigación (ANH)', 'value': 'KALEiv'},
                            {'label': ' Pozo Kalé - Inyector (ANH)', 'value': 'KALEy'},
                            {'label': ' Volúmenes de Monitoreo Kalé - Inyector (ANH)', 'value': 'KALEyv'},
                            {'label': ' Pozo Kalé - Captador (ANH)', 'value': 'KALEc'},
                            {'label': ' Pozo Platero - Investigación (ANH)', 'value': 'PLATEROi'},
                            {'label': ' Volúmenes de Monitoreo Platero - Investigación (ANH)', 'value': 'PLATEROiv'},
                            {'label': ' Pozo Platero - Inyector (ANH)', 'value': 'PLATEROy'},
                            {'label': ' Volúmenes de Monitoreo Platero - Inyector (ANH)', 'value': 'PLATEROyv'},
                            {'label': ' Pozo Platero - Captador (ANH)', 'value': 'PLATEROc'},
                            
                        ],
                        value=['KALEi'],
                        multi=True)],style={'font-size': '12px'}),
            html.Div([html.H4("Datos complementarios:", className="helps1 column"),
                      html.A(children=html.H5("?"),    
                             id='tCompl',
                             className="column helps2"
                             )
                      ],className='row flex-display',style={'marginBottom': 1, 'marginTop': 10}),  
            #html.H5("Información complementaria:", id='tCompl',className="card-subtitle",style= {"margin-top": "10px"}),
            dbc.Tooltip(
            "Selecciona otras capas de datos como complemento a los inicialmente desplegados en la gráfica 3D.",
            target="tCompl",
            ),
            html.Div(children=[dcc.Dropdown(id='PETRO',
                        placeholder="Variables a desplegar...",
                        style={'color': 'black'},
                        options=[
                            {'label': ' Pozos petrolíferos (UNAL-ANH-MINCIENCIAS)', 'value': 'POZO'},
                            {'label': ' Integridad Pozos - Kalé (ANH)', 'value': 'CRT_KALE'},
                            {'label': ' Campos petrolíferos (UNAL-ANH-MINCIENCIAS)', 'value': 'FIELD'},
                            #{'label': ' Trazo en superficie de líneas sísmicas (UNAL-ANH-MINCIENCIAS)', 'value': 'LIN'},
                            {'label': ' Rezumaderos (ANH)', 'value': 'REZ'},
                            {'label': ' Topes de pozos - Olini (ANH)', 'value': 'OLI'},
                            {'label': ' Direcciones de esfuerzos principales (WSM)', 'value': 'STRESS'},
                            {'label': ' Inyección de agua para recobro mejorado (ANH)', 'value': 'H2O'},
                            {'label': ' Inventario de puntos de agua (SGC)', 'value': 'HIDROGEO'},
                            {'label': ' Pozos de agua subterránea (SGC)', 'value': 'HIDROWELL'},
                            {'label': ' ANH-TR-2006-04-A (ANH) *', 'value': 'SEIS_1'},
                            {'label': ' CP-2010-1032 (ANH)*', 'value': 'SEIS_2'},
                            {'label': ' CP-2008-1385 (ANH)*', 'value': 'SEIS_3'},
                            {'label': ' CP-2008-1190 (ANH)', 'value': 'SEIS_4'},    
                        ],
                        value=[],
                        multi=True)],style={'font-size': '12px'}),
#------------Condicional campos--------
                html.Div(id='INY', children=[
                        html.H6("Campos (inyección de agua para recobro mejorado):", className="card-subtitle"),
                        # Create element to hide/show, in this case a slider
                        dcc.Dropdown(id='TINY',
                                    placeholder="Campo",
                                    style={'color': 'black'},
                                    options=[{'label':x,'value':x} for x in iny['CAMPO']],
                                    value='LA CIRA',
                                    multi=False,
                                    clearable=False
                                )

                    ],style= {'display': 'none',"margin-top": "10px",'font-size': '12px'}),
            html.Br(),
            dcc.Markdown('''
                    * ANH: Agencia Nacional de Hidrocarburos
                    * ECP: Ecopetrol
                    * MINCIENCIAS: Ministerio de Ciencia Tecnología e Innovación
                    * SGC: Servicio Geológico Colombiano
                    * UNAL: Universidad Nacional de Colombia
                    * IGAC: Instituto Geográfico Agustín Codazzi
                    * *¡Puede estar sujeto a tiempos de carga altos!
                '''),
            html.Br(),
            html.Button('¡Actualizar!', id='submit-val', n_clicks=0,style={'background-color': 'white',})
                    #  dbc.CardImg(src="assets\logos.png", bottom=True, alt='Logos_convenio_tripartito',)    
                 ], 
            
            className="sidebar",
            id='sidebar'
    # color="secondary",   # https://bootswatch.com/default/ for more card colors
    # inverse=True,

)

card_graph = html.Div(
        dcc.Graph(id='3d_model', figure={}), #className='pretty_container'
)

card_graph_profile = html.Div(
        dcc.Graph(id='Model_profile', figure={})
)

card_iny_graph = html.Div(
        dcc.Graph(id='Iny_graph', figure={})
)

references=[
        html.H2("Referencias", className="card-title"),
        html.H6("Agencia Nacional de Hidrocarburos - ANH & Servicio Geológico Colombiano - SGC (2016). Informe final del Convenio interadministrativo 194 ANH-014 SGC, entre la Agencia Nacional de Hidrocarburos y el Servicio Geológico Colombiano.", 
            className="card-text"),
        html.H6("Agencia Nacional de Hidrocarburos - ANH (2010). Mapa de Rezumaderos. Información Geológica y Geofísica. https://www.anh.gov.co/Informacion-Geologica-y-Geofisica/Estudios-Integrados-y-Modelamientos/Paginas/MAPA-DE-REZUMADEROS.aspx", 
            className="card-text"),
        html.H6("Agencia Nacional de Hidrocarburos - ANH (2021). INFORME CONCEPTO INTEGRIDAD DE POZOS CONTEMPLADOS EN EL ARTÍCULO 10, NUMERAL 14, PARÁGRAFO 3 DE LA RESOLUCIÓN DEL MINISTERIO DE MINAS Y ENERGÍA 40185 DEL 07 DE JULIO DE 2020. PROYECTO CEPI KALÉ. VICEPRESIDENCIA DE OPERACIONES, REGALIAS Y PARTICIPACIONES VICEPRESIDENCIA TECNICA.", 
            className="card-text"),          
        html.H6("Ángel-Martínez, C.E., Prieto-Gómez, G.A., Cristancho-Mejía, F., Sarmiento-Orjuela, A.M., Vargas-Quintero, J.A., Delgado-Mateus, C.J., Torres-Rojas, E., Castelblanco-Ossa, C.A., Camargo-Rache, G.L., Amazo-Gómez, D.F., Cipagauta-Mora, J.B., Lucuara-Reyes, E.D., Ávila-López, K.L. Fracica-González, L.R., Martín-Ravelo, A.S., Atuesta-Ortiz, D.A., Gracía-Romero, D.F., Triviño Cediel , R.J., Jaimes Villarreal, V.N., y Alarcón Rodríguez, W.F.(2021). Proyecto MEGIA: Modelo Geológico-Geofísico del Valle Medio del Magdalena. Producto No. 5. Bogotá: 192 pp.", 
            className="card-text"),
        html.H6("Dionicio, V., Mercado, O. y Lizarazo, M. (2020). Semáforo para el monitoreo sísmico durante el desarrollo de los proyectos piloto de investigación integral en yacimientos no convencionales de hidrocarburos en Colombia. Bogotá: Servicio Geológico Colombiano.", 
            className="card-text"),
        html.H6("Gómez, J. & Montes, N.E., compiladores. 2020. Mapa Geológico de Colombia 2020. Escala 1:1 000 000. Servicio Geológico Colombiano, 2 hojas. Bogotá.​", 
            className="card-text"),
        html.H6("Heidbach, O., M. Rajabi, X. Cui, K. Fuchs, B. Müller, J. Reinecker, K. Reiter, M. Tingay, F. Wenzel, F. Xie, M. O. Ziegler, M.-L. Zoback, and M. D. Zoback (2018): The World Stress Map database release 2016: Crustal stress pattern across scales. Tectonophysics, 744, 484-498, doi:10.1016/j.tecto.2018.07.007", 
            className="card-text"),
        html.H6("Heidbach, O., M. Rajabi, K. Reiter, M.O. Ziegler, and the WSM Team (2016): World Stress Map Database Release 2016. GFZ Data Services,doi:10.5880/WSM.2016.001", 
            className="card-text"),
        html.H6("Instituto Geográfico Agustin Codazzi - IGAC (2019). Base de datos vectorial básica. Colombia. Escala 1:100.000. Colombia en Mapas. https://www.colombiaenmapas.gov.co/#", 
            className="card-text"),
        html.H6("Servicio Geológico Colombiano. (2021). Banco de Información Petrolera. https://srvags.sgc.gov.co/JSViewer/GEOVISOR_BIP/", 
            className="card-text"),
        html.H6("Servicio Geológico Colombiano. (2022). Catálogo línea base de sismicidad: Valle Medio del Magdalena y La Loma Cesar. http://bdrsnc.sgc.gov.co/paginas1/catalogo/Consulta_Valle_Medio/valle_medio.php", 
            className="card-text"),
         html.H6("Tozer, B, Sandwell, D. T., Smith, W. H. F., Olson, C., Beale, J. R., & Wessel, P. (2019). Global bathymetry and topography at 15 arc sec: SRTM15+. Distributed by OpenTopography. https://doi.org/10.5069/G92R3PT9. Accessed: 2022-02-10", 
            className="card-text"),
    ]

# ls_k.extend(references)

card_function=dbc.Card(
    dbc.CardBody(ls_k
    ))

card_references=dbc.Card(
    dbc.CardBody(references
    ))

card_explication_sem=dbc.Card(
    dbc.CardBody([
        html.H2("¿Qué es el semáforo sísmico?", className="card-title"),
        html.H6("El semáforo sísmico es un mecanismo desarrollado por el Servicio Geológico Colombiano (SGC) para la toma de decisiones en el desarrollo de las operaciones de las Pruebas Piloto de Investigación Integral (PPII). Para el semáforo se han definido cuatro colores: verde, amarillo, naranja y rojo. Adicionalmente, se presenta enmarcado dentro de dos volúmenes cilíndricos denominados volúmen de monitoreo (correspondiente al cilíndro externo) y volúmen de suspensión (correspondiente al cilindro interno), definidos de acuerdo con la propuesta del semáforo sísmico (Dionicio et al., 2020). Los volumenes cilíndricos cuentan con una profundidad de 16 km,  radio interno de dos veces la profundidad medida del pozo (Dionicio et al., 2020) y externo de dos veces la profundidad medida del pozo más veinte kilómetros (2h + 20km), de acuerdo con la Resolución 40185 de 2020 del Ministerio de Minas y Energía.",
            className="card-text"),
        html.H6("La clasificación en colores del semáforo se realiza para cada uno de los diferentes rangos de magnitud de los eventos sísmicos que entren dentro de los volúmenes cilíndricos. Los rangos de magnitud son m0, m1, m2, m3 y m4, que tendrán diferentes estados del semáforo, son dependientes del número de sismos registrados diarios para cada uno de esos rangos, cuyos valores se comparan con los parámetros definidos en el documento propuesto para el semáforo sísmico, con el fin de obtener el correspondiente color del semáforo (Dionicio et al., 2020).", 
            className="card-text"),
        html.Div(
        html.Img(

                            src=app.get_asset_url("Tabla7a.png"),

                            id="Tabla7a-image",

                            style={

                                "height": "auto",
                                "max-width": "1000px",
                                "margin-top": "5px",
                                "display":"block",
                                "margin-left": "auto",
                                "margin-bottom": "5px",

                            },

                        )),
        html.Div(html.Img(

                            src=app.get_asset_url("Tabla7b.png"),

                            id="Tabla7b-image",

                            style={
                                "height": "auto",
                                "max-width": "1000px",
                                "margin-top": "5px",
                                "display":"block",
                                "margin-left": "auto",
                                "margin-bottom": "5px",
                            },

                        )),
        # dbc.CardImg(src="assets\Tabla7a.png", bottom=True, alt='Tabla7a',),
        # dbc.CardImg(src="assets\Tabla7b.png", bottom=True, alt='Tabla7b',),
        html.H6("Adicionalmente, a medida que se desarrolla el monitoreo diario de las actividades, se registra la acumulación de alertas para cada uno de los colores del semáforo sísmico, donde se asigna una puntuación para cada color de 0 para verde, 1 para amarillo y 3 para naranja (Dionicio et al., 2020). A partir de la puntuación acumulada mensual, se definen las acciones propuestas acordes con el esquema de puntuación del seguimiento mensual de sismicidad montoreada de los PPII (Dionicio et al., 2020).", 
            className="card-text"),
        html.Img(

                            src=app.get_asset_url("Tabla8.png"),

                            id="Tabla8-image",

                            style={
                                "height": "auto",
                                "max-width": "1000px",
                                "margin-top": "5px",
                                "display":"block",
                                "margin-left": "auto",
                                "margin-bottom": "5px",

                            },

                        ),
        #dbc.CardImg(src="assets\Tabla8.png", bottom=True, alt='Tabla8',),
    ]))

layout = dict(

    autosize=True,

    automargin=True,

    margin=dict(l=30, r=30, b=20, t=40),

    hovermode="closest",

    plot_bgcolor="#fcf9eb",

    paper_bgcolor="#fcf9eb",

    legend=dict(font=dict(size=10), orientation="h"),

)

app.layout = html.Div(
    [dcc.Store(id='toggle'),
     html.Div(

            [      
                html.Img(
                    src=app.get_asset_url("positivo_recortado.png"),
                    id="plotly-image",
                    className="logo-CdT"
                ),                   

                html.H3(

                    "Modelo Tridimensional del Valle Medio del Magdalena - PPII",
                    className="model-title"

                    # style={"margin-bottom": "0px", 'textAlign': 'center','font-weight':'bold'},
                ), 

            ], className="header", id='header'

            ),
            
        html.Div(
            [
                html.Div(
            [
                dcc.Loading(
                id="loading-1",
                type="cube",
                fullscreen=True,
                style={'backgroundColor': 'black','opacity':'0.4'},
                children=html.Div(id="loading-output-1"),
                debug=False,
                loading_state={'component_name':'Cargando...',
                            'prop_name':'Cargando...',
                            'is_loading':True}),
                card_main,

                

                html.Div(
                    [
                        html.Br(),
                     dbc.Button(html.I(), color='primary', id='btn_sidebar', size="lg"),
                    html.Div(card_graph),
                         ],
                    className="model_graph column",
                                id = 'content'
                                ),
            ],
            # justify="start",

            ),
            ], className="row flex-display",
            id = 'div_slider'
        ),
        html.Hr(),           
        html.Div(
                [       html.Div([html.H5('Perfil:',className='profile column'),
                                    dbc.Button('¿Cómo funciona?',outline=True,color='info',
                                    id='perf_but',className='me-2 help',n_clicks=0)],className='btn-title-row'),
                            dbc.Tooltip(
                            "El perfil sísmico permite visualizar los sismos, la topografía, las superficies geológicas, lo pozos PPII y los volúmenes de monitoreo contenidos en un perfil de 0.1°. Estos pueden ser desactivados en la interfaz derecha, así como la especificar la información pasando el cursor encima.",
                            target='perf_but',
                            ),
                        html.Div(card_graph_profile),
                        html.Hr(),
                               html.Div([html.H5('Inyección de agua para recobro mejorado en campos de hidrocarburos (ANH):',className='profile column'),
                                    dbc.Button('¿Cómo funciona?',outline=True,color='info',
                                    id='iny_but',className='me-2 help',n_clicks=0)],className='btn-title-row'),
                            dbc.Tooltip(
                            "La grafica de la izquierda indica la evolución temporal de la inyeccion de agua en un campo petrolífero en específico, el cual puede ser modificado en la sección de informacion complementaria. La de la derecha, indica como es esta inyeccion por campo cada año. ",
                            target='iny_but',
                            ),
                        html.Div([card_iny_graph, dcc.Graph(figure = iny_bar)], id = "graficas_iny")
                    ], 
            #  justify="start"
            ),
        html.Div([
                 html.Div(
                     [     
        dbc.Button("¿Cómo funciona?", color="#4cb286",id="function_but_xl", size="sm",className="me-1", n_clicks=0),
        dbc.Button("¿Semáforo sísmico?",color="#4cb286", id="semaforo_but_xl",size="sm", className="me-1", n_clicks=0),
        dbc.Button("Referencias",color="#4cb286", id="references_but_xl",size="sm", className="me-1", n_clicks=0)
        ], className='helpButtons'
        ),
                 html.Hr(),
                 html.Img(
                    src=app.get_asset_url("Institucional_3Logos_letrasblancas.png"),
                    id="logos-image"),
            ],id='footer'),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(" ")),
                dbc.ModalBody(card_function),
            ],
            id="function_mod_xl",
            fullscreen=True,
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(" ")),
                dbc.ModalBody(card_references),
            ],
            id="references_mod_xl",
            fullscreen=True,
            is_open=False,
        ),
                dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(" ")),
                dbc.ModalBody(card_explication_sem),
            ],
            id="semaforo_mod_xl",
            fullscreen=True,
            is_open=False,
        ),


        
        # html.Div(
        #         [
        #             html.Div(children=card_references)
        #             ], 
        #     #  justify="start"
        #     )      
    ],
style={"display": "flex", "flex-direction": "column"},)

def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

# app.callback(
#     dash.dependencies.Output("perf_mod", "is_open"),
#     dash.dependencies.Input("perf_but", "n_clicks"),
#     dash.dependencies.State("perf_mod", "is_open"),
# )(toggle_modal)

# app.callback(
#     dash.dependencies.Output("iny_mod", "is_open"),
#     dash.dependencies.Input("iny_but", "n_clicks"),
#     dash.dependencies.State("iny_mod", "is_open"),
# )(toggle_modal)

app.callback(
    dash.dependencies.Output("function_mod_xl", "is_open"),
    dash.dependencies.Input("function_but_xl", "n_clicks"),
    dash.dependencies.State("function_mod_xl", "is_open"),
)(toggle_modal)

app.callback(
    dash.dependencies.Output("references_mod_xl", "is_open"),
    dash.dependencies.Input("references_but_xl", "n_clicks"),
    dash.dependencies.State("references_mod_xl", "is_open"),
)(toggle_modal)

app.callback(
    dash.dependencies.Output("semaforo_mod_xl", "is_open"),
    dash.dependencies.Input("semaforo_but_xl", "n_clicks"),
    dash.dependencies.State("semaforo_mod_xl", "is_open"),
)(toggle_modal)

@app.callback(
     [dash.dependencies.Output(component_id='3d_model', component_property='figure'),
      dash.dependencies.Output(component_id='DATE', component_property='initial_visible_month'),
      dash.dependencies.Output(component_id='GREAL', component_property='style'),
      dash.dependencies.Output(component_id='COLORADO', component_property='style'),
      dash.dependencies.Output(component_id='MUGROSA', component_property='style'),
      dash.dependencies.Output(component_id='CHORROS', component_property='style'),
      dash.dependencies.Output(component_id='EOCMED', component_property='style'),
        dash.dependencies.Output(component_id='PAJA', component_property='style'),
      dash.dependencies.Output(component_id='SALADA', component_property='style'),
      dash.dependencies.Output(component_id='SIMITI', component_property='style'),
      dash.dependencies.Output(component_id='GALEMBO', component_property='style'),
      dash.dependencies.Output(component_id='CIRASHALE', component_property='style'),
      dash.dependencies.Output(component_id='BAGRE', component_property='style'),
      dash.dependencies.Output(component_id='CHONTORALES', component_property='style'),
      dash.dependencies.Output(component_id='COLORADOH', component_property='style'),
      dash.dependencies.Output(component_id='ENREJADO', component_property='style'),
      dash.dependencies.Output(component_id='ESMERALDAS', component_property='style'),
      dash.dependencies.Output(component_id='HIEL', component_property='style'),
      dash.dependencies.Output(component_id='LLUVIA', component_property='style'),
      dash.dependencies.Output(component_id='MUGROSAH', component_property='style'),
      dash.dependencies.Output(component_id='INY', component_property='style'),
      dash.dependencies.Output("loading-output-1", "children")
      ],



    [dash.dependencies.Input('submit-val', 'n_clicks'),
     dash.dependencies.State(component_id='TOPO', component_property='value'),
     dash.dependencies.State(component_id='EXG', component_property='value'),
     dash.dependencies.State(component_id='DATE', component_property='start_date'),
     dash.dependencies.State(component_id='DATE', component_property='end_date'),
     dash.dependencies.State(component_id='MAGN', component_property='value'),
     dash.dependencies.State(component_id='DEPTH', component_property='value'),
     dash.dependencies.State(component_id='SEISMO', component_property='value'),
     dash.dependencies.State(component_id='PPII', component_property='value'),
     dash.dependencies.State(component_id='CART', component_property='value'),
     dash.dependencies.State(component_id='PETRO', component_property='value'),
     dash.dependencies.State(component_id='GEOL', component_property='value'),
     dash.dependencies.State(component_id='Longitud 1', component_property='value'),
     dash.dependencies.State(component_id='Longitud 2', component_property='value'),
     dash.dependencies.State(component_id='Latitud 1', component_property='value'),
     dash.dependencies.State(component_id='Latitud 2', component_property='value'),
     dash.dependencies.State(component_id='TGREAL', component_property='value'),
     dash.dependencies.State(component_id='TCOLORADO', component_property='value'),
     dash.dependencies.State(component_id='TMUGROSA', component_property='value'),
     dash.dependencies.State(component_id='TCHORROS', component_property='value'),
     dash.dependencies.State(component_id='TEOCMED', component_property='value'),
     dash.dependencies.State(component_id='TPAJA', component_property='value'),
     dash.dependencies.State(component_id='TSALADA', component_property='value'),
     dash.dependencies.State(component_id='TSIMITI', component_property='value'),
     dash.dependencies.State(component_id='TGALEMBO', component_property='value'),
     dash.dependencies.State(component_id='TCIRASHALE', component_property='value'),
     dash.dependencies.State(component_id='TBAGRE', component_property='value'),
     dash.dependencies.State(component_id='TCHONTORALES', component_property='value'),
     dash.dependencies.State(component_id='TCOLORADOH', component_property='value'),
     dash.dependencies.State(component_id='TENREJADO', component_property='value'),
     dash.dependencies.State(component_id='TESMERALDAS', component_property='value'),
     dash.dependencies.State(component_id='THIEL', component_property='value'),
     dash.dependencies.State(component_id='TLLUVIA', component_property='value'),
     dash.dependencies.State(component_id='TMUGROSAH', component_property='value'),
     
     ])

def update_figure(n_clicks,TOPO,EXG,START_DATE,END_DATE,MAGN,DEPTH,SEISMO,PPII,CART,PETRO,GEOL,x0,x1,y0,y1,
                        TGREAL,TCOLORADO,TMUGROSA,TCHORROS,TEOCMED,TPAJA,TSALADA,TSIMITI,TGALEMBO,TCIRASHALE,
                        TBAGRE,TCHONTORALES,TCOLORADOH,TENREJADO,TESMERALDAS,THIEL,TLLUVIA,TMUGROSAH):
        sub=None
        fig=go.Figure()
        
        if np.isin('H2O', PETRO):
            INYO={'display': 'block'}
            # iny=pd.read_csv(r'datasets\inyeccion_geo.csv',delimiter=';',decimal=',')
            # iny=iny[:-1]
            ls_form=[False]*len(iny['CAMPO'])
            ls_form[-1]=True
            for i,_ in zip(iny['CAMPO'],ls_form):
                    inyc=iny[iny['CAMPO']==i]
                    fig.add_trace(go.Scatter3d(x=[float(inyc['X'])]*2, y=[float(inyc['Y'])]*2, z=[0,-1*float(inyc['prof'])],
                                hovertemplate=[inyc['CAMPO'].astype(str)+'<br>'
                                        'Pozos:'+inyc['POZOS'].astype(str)+'<br>'
                                        'BBL:'+inyc['TOTAL_bbl'].astype(str)]*2,mode='lines',name=str(i),
                                        line=dict(color=inyc['TOTAL_bbl'],
                                    width=20,colorscale='Jet',
                                cmax=((iny['TOTAL_bbl'])).max(),
                                cmin=((iny['TOTAL_bbl'])).min(),
                                )
                                ,showlegend=False),)
        else:
            INYO={'display': 'none'}
        if np.isin('GEO', GEOL):
            if TOPO==0:
                DISM=0
            else:
                DISM=0.01
            topog.colorscale=['black','black']
            topog.opacity=TOPO-DISM
            fig.add_trace(topog,row=sub,col=sub)
            for i in df_geos['name'].unique():
                name=i.replace('_','?')
                df_1=df_colors_geo[df_colors_geo['SimboloUC']==name]
                df_geos_1=df_geos[df_geos['name']==i]
                text='Edad: '+np.array(df_1['Edad'].astype(str))[0]+'<br>Descripción: '+np.array(df_1['Descripcio'].astype(str))[0]
                text=str(text)
                fig.add_trace(geology_super(df_geos_1,np.array(df_1['Color'].astype(str))[0],name,text,TOPO))
            del i
            
        else:
            if TOPO>0:
                topog.colorscale=['green','greenyellow','saddlebrown','saddlebrown','saddlebrown','saddlebrown','snow','snow']
                topog.opacity=TOPO
                fig.add_trace(topog,row=sub,col=sub)
            else:
                pass
        df_sismos_1=df_sismos[(df_sismos['FECHA - HORA UTC']<=END_DATE)&(df_sismos['FECHA - HORA UTC']>=START_DATE)&
        (df_sismos['MAGNITUD']>=MAGN[0])&(df_sismos['MAGNITUD']<=MAGN[1])
        &(df_sismos['PROF. (m)']>=(DEPTH[1]*-1))&(df_sismos['PROF. (m)']<=(DEPTH[0]*-1))]
        text=text_scatter(SEISMO,df_sismos_1)
        if np.isin('SISM',SEISMO):
            vis=True
        else :
            vis=False
        if np.isin('ERROR', SEISMO):
            err=True
        else:
            err=False
        fig.add_trace(go.Scatter3d(
            x=df_sismos_1['LONGITUD (°)'],y=df_sismos_1['LATITUD (°)'],z=df_sismos_1['PROF. (m)'],mode='markers',
            
            marker=dict(
                size=(df_sismos_1['MAGNITUD'])**2,
                color=df_sismos_1['PROF. (m)'],                # set color to an array/list of desired values
                colorscale='Jet',   # choose a colorscale
                opacity=0.8,
                cmax=df_sismos['PROF. (m)'].max(),
                cmin=-32000,
                #showscale=True,
                #colorbar={"title": 'Profundidad del <br> sismo (m)',
                #    "orientation": 'h'},
            ),
            error_x=dict(
                array=df_sismos_1['ERROR LONGITUD (°)'],                # set color to an array/list of desired values
                color='red',   # choose a colorscale
                symmetric=True,
                width=0.01,
                visible=err
            ),
            error_y=dict(
                array=df_sismos_1['ERROR LATITUD (°)'],                # set color to an array/list of desired values
                color='red',   # choose a colorscale
                symmetric=True,
                width=0.01,
                visible=err
            ),
            error_z=dict(
                array=df_sismos_1['ERROR PROFUNDIDAD SUP (m)'], 
                arrayminus=df_sismos_1['ERROR PROFUNDIDAD (m)'] ,             
                color='red',   # choose a colorscale
                symmetric=False,
                width=0.01,
                visible=err
            ),
            hovertemplate=text,
                name='Sismos',
                showlegend=False,
                visible=vis
                ),row=sub,col=sub)

        if np.isin('KALEi', PPII):
            fig.add_traces([kalei,kale_vert,kale_hort])
        if np.isin('KALEiv', PPII):
            fig.add_traces([kicyl1,kibcircles1,kicyl2,kibcircles2,kicyl3,kibcircles3])
        if np.isin('KALEy', PPII):
            fig.add_traces([kaley,kale_iny_tray])
        if np.isin('KALEyv', PPII):
            fig.add_traces([kycyl1,kybcircles1,kycyl2,kybcircles2,kycyl3,kybcircles3])
        if np.isin('KALEc', PPII):
            fig.add_traces([kalec,kale_cap_tray])
        if np.isin('PLATEROi', PPII):
            fig.add_traces([plai,plat_vert,plat_hort])
        if np.isin('PLATEROiv', PPII):
            fig.add_traces([picyl1,pibcircles1,picyl2,pibcircles2,picyl3,pibcircles3])
        if np.isin('PLATEROy', PPII):
            fig.add_traces([play,plat_iny_tray])
        if np.isin('PLATEROyv', PPII):
            fig.add_traces([pycyl1,pybcircles1,pycyl2,pybcircles2,pycyl3,pybcircles3])
        if np.isin('PLATEROc', PPII):
            fig.add_traces([plac,plat_cap_tray])

        if np.isin('RIV', CART):
            fig.add_traces(rivers_ls)
        if np.isin('STA', CART):
            fig.add_trace(STA_VMM)
            fig.add_trace(STA_LOM)
        if np.isin('VIA', CART):
            fig.add_traces(roads_ls)
        if np.isin('POZO', PETRO):
            fig.add_trace(Pozos)
            # fig.add_traces(pozos_ls)
        if np.isin('CRT_KALE', PETRO):
            fig.add_trace(criticidad)
            fig.add_traces(well_criticidad)
        if np.isin('REZ', PETRO):
            fig.add_trace(rez)
        if np.isin('OLI', PETRO):
            fig.add_traces(ol_ls)
        if np.isin('STRESS', PETRO):
            fig.add_traces(st_ls)
        #-------
        if np.isin('SEIS_1', PETRO):
            fig.add_trace(sismica_1)
        if np.isin('SEIS_2', PETRO):
            fig.add_trace(sismica_2)
        if np.isin('SEIS_3', PETRO):
            fig.add_trace(sismica_3)
        if np.isin('SEIS_4', PETRO):
            fig.add_trace(sismica_4)
        #---------
        if np.isin('POB', CART):
                fig.add_trace(Poblaciones)
                # fig.update_layout(
                # scene=dict(
                # annotations=Pobl),
                # # overwrite=False,
                # font_family="Poppins")
        if np.isin('FIELD', PETRO):
            fig.add_traces(campet_ls)
            fig.update_layout(
            scene=dict(
            annotations=inyec),
            # overwrite=False,
            font_family="Poppins")
        # if (np.isin('POB', CART)) and (np.isin('FIELD', PETRO)):
        #     inpo=[]
        #     for i in inyec:
        #         inpo.append(i)
        #     for i in Pobl:
        #         inpo.append(i)
        #     # print(inyec)
        #     # print(Pobl)
        #     # inpo=inyec.extend(Pobl)
        #     # print(inpo)
        #     fig.update_layout(
        #     scene=dict(
        #     annotations=inpo),
        #     # overwrite=False,
        #     font_family="Poppins")
        if np.isin('FALL', GEOL):
            fig.add_traces(fallas_ls)
        if np.isin('REAL', GEOL):
                Real.opacity=TGREAL
                fig.add_trace(Real)
                grealo={'display': 'block'}
        else:
            grealo={'display': 'none'}

        if np.isin('COL', GEOL):
                Colorado.opacity=TCOLORADO
                fig.add_trace(Colorado)
                coloradoo={'display': 'block'}
        else:
            coloradoo={'display': 'none'}       
        if np.isin('MUG', GEOL):
                Mugrosa.opacity=TMUGROSA
                fig.add_trace(Mugrosa)
                mugrosao={'display': 'block'}
        else:
            mugrosao={'display': 'none'}
        if np.isin('CHO', GEOL):
                Chorros.opacity=TCHORROS
                fig.add_trace(Chorros)
                chorroso={'display': 'block'}
        else:
            chorroso={'display': 'none'}
        if np.isin('EOC', GEOL):
                Eoceno.opacity=TEOCMED
                fig.add_trace(Eoceno)
                eocmedo={'display': 'block'}
        else:
            eocmedo={'display': 'none'}
#PAJA
        if np.isin('PAJA', GEOL):
                        paja.opacity=TPAJA
                        fig.add_trace(paja)
                        pajao={'display': 'block'}
        else:
            pajao={'display': 'none'}
        #Salada
        if np.isin('SALADA', GEOL):
                        salada.opacity=TSALADA
                        fig.add_trace(salada)
                        salado={'display': 'block'}
        else:
            salado={'display': 'none'}
        #Simiti
        if np.isin('SIMITI', GEOL):
                        simiti.opacity=TSIMITI
                        fig.add_trace(simiti)
                        simitio={'display': 'block'}
        else:
            simitio={'display': 'none'}
        #Galembo
        if np.isin('GALEMBO', GEOL):
                        galembo.opacity=TGALEMBO
                        fig.add_trace(galembo)
                        galemboo={'display': 'block'}
        else:
            galemboo ={'display': 'none'}
        #CiraShale
        if np.isin('CIRASHALE', GEOL):
                        ciraShale.opacity=TCIRASHALE
                        fig.add_trace(ciraShale)
                        ciraShaleo={'display': 'block'}
        else:
            ciraShaleo ={'display': 'none'}
        #Bagre
        if np.isin('BAGRE', GEOL):
                        bagre.opacity=TBAGRE
                        fig.add_trace(bagre)
                        bagreo={'display': 'block'}
        else:
            bagreo ={'display': 'none'}
        #Chontorales
        if np.isin('CHONTORALES', GEOL):
                        chontorales.opacity=TCHONTORALES
                        fig.add_trace(chontorales)
                        chontoraleso={'display': 'block'}
        else:
            chontoraleso ={'display': 'none'}
        #Coloradoh
        if np.isin('COLORADOH', GEOL):
                        colorado.opacity=TCOLORADOH
                        fig.add_trace(colorado)
                        coloradoho={'display': 'block'}
        else:
            coloradoho ={'display': 'none'}
        #Enrejado
        if np.isin('ENREJADO', GEOL):
                        enrejado.opacity=TENREJADO
                        fig.add_trace(enrejado)
                        enrejadoo={'display': 'block'}
        else:
            enrejadoo ={'display': 'none'}
        #Esmeraldas
        if np.isin('ESMERALDAS', GEOL):
                        esmeraldas.opacity=TESMERALDAS
                        fig.add_trace(esmeraldas)
                        esmeraldaso={'display': 'block'}
        else:
            esmeraldaso ={'display': 'none'}
        #Hiel
        if np.isin('HIEL', GEOL):
                        hiel.opacity=THIEL
                        fig.add_trace(hiel)
                        hielo={'display': 'block'}
        else:
            hielo ={'display': 'none'}
        #Lluvia
        if np.isin('LLUVIA', GEOL):
                        lluvia.opacity=TLLUVIA
                        fig.add_trace(lluvia)
                        lluviao={'display': 'block'}
        else:
            lluviao ={'display': 'none'}
        #Galembo
        if np.isin('MUGROSAH', GEOL):
                        mugros.opacity=TMUGROSAH
                        fig.add_trace(mugros)
                        mugrosaho={'display': 'block'}
        else:
            mugrosaho ={'display': 'none'}
        #End Geology
        if np.isin('HIDROGEO', PETRO):
                fig.add_trace(hidrogeo)
        if np.isin('HIDROWELL', PETRO):
                fig.add_trace(hidro_wells)
                fig.add_traces(hw_ls)
        if np.isin('PER', CART):
                fig.add_trace(profile_plane(x0,y0,x1,y1))
        if np.isin('g1', GEOL):
                fig.add_traces(g2)
        if np.isin('g2', GEOL):
                fig.add_traces(g1)
        if np.isin('g3', GEOL):
                fig.add_traces(g3)
        fig.update_layout(autosize = True, height=600, 
                            margin=dict(l=0, r=0, b=0, t=0),plot_bgcolor='rgb(0,0,0)',
                            font_family="Poppins"
                        )
        fig.update_layout(
        scene = dict(aspectratio=dict(x=1,y=1.785714286,z=(42000/155540)*EXG),
                xaxis = dict(title='Longitud(°)',nticks=10, range=[loi,los]),
                yaxis = dict(title='Latitud(°)',nticks=10, range=[lai,las],),
                zaxis = dict(title='Profundidad (m)',nticks=10, range=[-32000,10000],),),
        font_family="Poppins")
        fig.update_layout(legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01,
                ), font_family="Poppins",)
    
        

        camera = dict(
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=-1, y=-1, z=2)
                )

        fig.update_layout(scene_camera=camera, font_family="Poppins",
        # title=dict(
        #     font='Poppins',
        #     size='12rem',
        #     y='0',
        #     x='1'
        # ),
        hoverlabel=dict(
                        # bgcolor="white",
                        font_size=12,
                        font_family="Poppins"
                    ),
                    title_font_size=12,
                        title={
                        'text': "*Sistema de coordenadas: WGS 84",
                        'y':0.9,
                        'x':0.9,
                        'xanchor': 'right',
                        'yanchor': 'top',}
                        )
        
        loading=time.sleep(1)
        return fig,START_DATE,grealo,coloradoo,mugrosao,chorroso,eocmedo,pajao,salado,simitio,galemboo,ciraShaleo,bagreo,chontoraleso,coloradoho,enrejadoo,esmeraldaso,hielo,lluviao,mugrosaho,INYO,loading

@app.callback(
    [dash.dependencies.Output('sidebar', 'className'),
     dash.dependencies.Output('content', 'className'),
     dash.dependencies.Output('toggle', 'data'),
     dash.dependencies.Output('btn_sidebar','className')
     ], 
    [dash.dependencies.Input('btn_sidebar', 'n_clicks'),
     dash.dependencies.Input('toggle', 'data')]    
     )

def toggle_sidebar(n, n_clicks):
    if n:
        if n_clicks == 'show':
            sidebar_classname = 'sidebar_hidden'
            content_classname = 'content_sidebar_hidden'
            c_clicks = 'hidden'
            btn_sidebar_className = 'bi bi-arrow-bar-right'            
        if n_clicks == 'hidden':
            sidebar_classname = 'sidebar'
            content_classname = 'model_graph'
            c_clicks = 'show'
            btn_sidebar_className = 'bi bi-arrow-bar-left' 
    else:
        sidebar_classname = 'sidebar'
        content_classname = 'model_graph'
        c_clicks = 'show'
        btn_sidebar_className = 'bi bi-arrow-bar-left' 
    return sidebar_classname, content_classname, c_clicks, btn_sidebar_className
    
@app.callback(
     dash.dependencies.Output(component_id='Model_profile', component_property='figure'),



    [dash.dependencies.Input('submit-val', 'n_clicks'),
     dash.dependencies.State(component_id='DATE', component_property='start_date'),
     dash.dependencies.State(component_id='DATE', component_property='end_date'),
     dash.dependencies.State(component_id='MAGN', component_property='value'),
     dash.dependencies.State(component_id='DEPTH', component_property='value'),
     dash.dependencies.State(component_id='SEISMO', component_property='value'),
     dash.dependencies.State(component_id='Longitud 1', component_property='value'),
     dash.dependencies.State(component_id='Longitud 2', component_property='value'),
     dash.dependencies.State(component_id='Latitud 1', component_property='value'),
     dash.dependencies.State(component_id='Latitud 2', component_property='value') ])

def update_profile(n_clicks,START_DATE,END_DATE,MAGN,DEPTH,SEISMO,x0,x1,y0,y1):
    #Perfil sismico'----------------------------------------------------------------------------------------------------------------
    df_sismos_1=df_sismos[(df_sismos['FECHA - HORA UTC']<=END_DATE)&(df_sismos['FECHA - HORA UTC']>=START_DATE)&
    (df_sismos['MAGNITUD']>=MAGN[0])&(df_sismos['MAGNITUD']<=MAGN[1])
    &(df_sismos['PROF. (m)']>=(DEPTH[1]*-1))&(df_sismos['PROF. (m)']<=(DEPTH[0]*-1))]
    df_sismos_1['Unnamed: 0']=[i for i in range(0,len(df_sismos_1))]
    fig2= go.Figure()
    df_profile,dist_max=profile(x0,x1,y0,y1,df_sismos_1,'sismos')
    pozos_ppii=pd.DataFrame({
    'name':['Kalé - Investigación','Kalé - Inyector',
            'Platero - Investigación','Platero - Inyector',
            'Kalé - Captador','Platero - Captador'],
    'lon':[-73.8566,-73.8571014,-73.89389,-73.8944016,-73.8570023,-73.8943024],
    'lat':[7.36551,7.3647799,7.2572498,7.25667,7.3647499,7.2566800],
    'z':[69]*6,
    'TVD':[3902,2618.232,3227.8,2325.6,2325.6,2325.6],
    'color':['blue','aqua','red','orange','orange','gold']})
    ppii_profile,dist=profile(x0,x1,y0,y1,pozos_ppii,"pozos",)
    cilindro_2d=semaforo_profile(x0,x1,y0,y1,pozos_ppii)
    try:
        fig2.add_traces(go.Scatter(x=ppii_profile['DIST'],
                                    y=ppii_profile['z'],
                                    mode ='markers',
                                    marker = dict(color=ppii_profile['color'], size=8),
                                    name='Pozos PPII',
                                    hovertemplate=ppii_profile['name'],
                                    marker_symbol='star',
                                    error_y=dict(
                                                    array=[0]*len(ppii_profile['DIST']), 
                                                    arrayminus=ppii_profile['TVD'].values ,             
                                                    color='green',   # choose a colorscale
                                                    symmetric=False,
                                                    width=0.1,
                                                    visible=True
                                                ),))
    except:
        pass
       
    text1=text_scatter(SEISMO,df_profile)
    profiles=go.Scatter(x=df_profile['DIST'],
                                y=df_profile['PROF. (m)'],
                                mode='markers',
                                name='Sismos',
                                error_y=dict(
                                    array=df_profile['ERROR PROFUNDIDAD SUP (m)'],                # set color to an array/list of desired values
                                    color='red',   # choose a colorscale
                                    symmetric=True,
                                    thickness=0.1,
                                    arrayminus=df_profile['ERROR PROFUNDIDAD (m)']
                                ),
                                marker=dict(size=df_profile['MAGNITUD']*5,
                                            color=df_profile['PROF. (m)'],
                                            colorscale='Jet',   # choose a colorscale
                                            opacity=0.8,
                                            cmax=100,
                                            cmin=-32000,),
                                            hovertemplate=text1)
    seismic_scale=go.Scatter(x=[dist_max*0.93,dist_max*0.94,dist_max*0.955,dist_max*0.975,dist_max],
                                y=[-40000]*5,
                                 hoverinfo='text',
                                hovertext=np.array(['1','2','3','4','5']),
                                mode='markers',
                                name='Magnitudes',
                                showlegend=False,
                                marker=dict(size=(np.array([1,2,3,4,5])*5),
                                            opacity=0.8,
                                            ))
    for x_t,t_t in zip([dist_max*0.93,dist_max*0.94,dist_max*0.955,dist_max*0.975,dist_max],['1','2','3','4','5']):
        fig2.add_annotation(x=x_t, y=-35400,hovertext=t_t,
            text=t_t,
            showarrow=False,
            yshift=0,
            
        font=dict(
            family="Poppins",
            size=12,
            
            )),
    fig2.add_trace(seismic_scale)  
    if dist_max>=2:
        scale_num=15;scale_text='15';scale_size=12
    elif dist_max<2 and dist_max>=1:
        scale_num=10;scale_text='10';scale_size=12
    else :
        scale_num=5;scale_text='5';scale_size=12
    fig2.add_annotation(x=(scale_num/111.1)/2, y=-38000,hovertext=scale_text+' km',
                text=scale_text+'km',
                showarrow=False,
                yshift=0,
            font=dict(
                family="Poppins",
                size=scale_size,
                
                ))
    fig2.add_trace(go.Scatter(x=np.linspace(0, scale_num/111.1, 4), y=np.array([-40000]*4),
                hovertext='Escala',
                mode='lines',
                name=scale_text+'km',
                showlegend=False,
                hoverinfo='text',
                marker=dict(color='black', size=8)))
    fig2.add_trace(go.Scatter(x=np.linspace(scale_num/111.1, scale_num*2/111.1, 4), y=np.array([-40000]*4),
                hovertext='Escala',
                mode='lines',
                hoverinfo='text',
                name=scale_text+'km',
                showlegend=False,
                marker=dict(color='white', size=8)))
    fig2.add_trace(go.Scatter(x=np.linspace(scale_num*2/111.1, scale_num*3/111.1, 4), y=np.array([-40000]*4),
                hovertext='Escala',
                mode='lines',
                hoverinfo='text',
                name=scale_text+'km',
                showlegend=False,
                marker=dict(color='black', size=8)))
    fig2.add_trace(go.Scatter(x=np.linspace(scale_num*3/111.1, scale_num*4/111.1, 4), y=np.array([-40000]*4),
                hovertext='Escala',
                hoverinfo='text',
                mode='lines',
                name=scale_text+'km',
                showlegend=False,
                marker=dict(color='white', size=8)))
    fig2.add_trace(go.Scatter(x=np.linspace(scale_num*4/111.1, scale_num*5/111.1, 4), y=np.array([-40000]*4),
                hovertext='Escala',
                hoverinfo='text',
                mode='lines',
                name=scale_text+'km',
                showlegend=False,
                marker=dict(color='black', size=8)))
    fig2.add_trace(profiles)      
    t_profile=topo_profile(x0,x1,y0,y1,df_topo)
    fig2.add_trace(t_profile)  
    Eoceno_1=geologic_profile(x0,y0,x1,y1,'datasets/DISCORDANCIA_EOCENO.txt','Discordancia del Eoceno Medio','#FDA75F',[2,3,4],';',',')
    Real_1=geologic_profile(x0,y0,x1,y1,'datasets/BASE_CUATERNARIO.txt','Tope Grupo Real','#FFFF00',[2,3,4],';',',')
    Chorros_1=geologic_profile(x0,y0,x1,y1,'datasets/TOPE_CHORROS.txt','Tope Grupo Chorros','#974d02',[2,3,4],';',',')
    Colorado_1=geologic_profile(x0,y0,x1,y1,'datasets/TOPE_COLORADO.txt','Tope Formación Colorado','#FEC07A',[2,3,4],';',',')
    Mugrosa_1=geologic_profile(x0,y0,x1,y1,'datasets/TOPE_MUGROSA.txt','Tope Formación Mugrosa','#b34400',[2,3,4],';',',')
    Paja_1=geologic_profile(x0,y0,x1,y1,'datasets/PAJA_SGC_TVDSS_3.xyz','Tope Formación Paja','#8CCD57',['lon','lat','Z'],',','.')
    Salada_1=geologic_profile(x0,y0,x1,y1,'datasets/SALADA_SGC_TVDSS_3.xyz','Tope Formación Salada','#BFE35D',['lon','lat','Z'],',','.')
    Simiti_1=geologic_profile(x0,y0,x1,y1,'datasets/SIMITI_SGC_TVDSS_3.xyz','Tope Formación Simiti','#BFE48A',['lon','lat','Z'],',','.')
    Galembo_1=geologic_profile(x0,y0,x1,y1,'datasets/GALEMBO_SGC_TVDSS_3.xyz','Tope Formación Galembo','#E6F47F',['lon','lat','Z'],',','.')
    
    p1,p2=orientation(x0,y0,x1,y1)

    fig2.add_annotation(x=0, y=10000,
        text=p1,
        showarrow=False,
        yshift=0,
    font=dict(
        family="Poppins",
        size=25,
        ))
    fig2.add_annotation(x=dist_max, y=10000,
        text=p2,
        showarrow=False,
        font=dict(
        family="Poppins",
        size=25,
        ),
        yshift=0)
        #,Paja_1,Salada_1,Simiti_1,Galembo_1
    fig2.add_traces(data=[Real_1,Colorado_1,Mugrosa_1,Chorros_1,Eoceno_1,Galembo_1,Salada_1,Simiti_1,Paja_1]) 
    try:
        fig2.add_traces(cilindro_2d)
    except:
        pass 
    fig2.update_layout(
                # title="Perfil",
                font_family="Poppins",
        hoverlabel=dict(
                        # bgcolor="white",
                        font_size=12,
                        font_family="Poppins"
                    ),
            ),
    fig2.update_layout(xaxis_title="Distancia (°)",
                        yaxis_title="Profundidad (m)",
                        font_family="Poppins",
                        margin=dict(t=50,l=50,b=50,r=50), showlegend = False)
    return fig2

@app.callback(
     dash.dependencies.Output(component_id='Iny_graph', component_property='figure'),
    [dash.dependencies.Input('submit-val', 'n_clicks'),
    dash.dependencies.State(component_id='TINY', component_property='value')])

def iny(n_clsick,TINY):
    datos_iny = pd.read_csv("datasets/inyeccion_geo.csv", delimiter = ';')
    name_campo=TINY
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"type": "scatter"}]],
        subplot_titles=('Volúmenes de agua (bbl) - '+name_campo))
    months=[]
    for i in datos_iny.columns:
        if '-' in i:
            months.append(i)
    del i
    # name_campo='LA CIRA'
    iny_df=datos_iny[datos_iny['CAMPO']==name_campo]

    fig.add_trace(
        go.Scatter(x=months,y=[float(np.array(iny_df[x])[0]) for x in months],name=name_campo,showlegend=False),
        row=1, col=1
    )
    años=np.arange(2017,2022)
    old=np.array([0,0,0,0,0])
    fig.update_layout(margin=dict(t=50,l=50,b=50,r=50),hoverlabel=dict(
                        # bgcolor="white",
                        font_size=12,
                        font_family="Poppins"
                    ),barmode='stack',
                    # title_text="Inyección de agua para recobro mejorado en campos de hidrocarburos (ANH)", 
                    font_family="Poppins")
    fig.update_yaxes(tickvals=np.arange(0,300000000+1,50000000))
    fig.update_xaxes(tickvals=años)
    fig.update_xaxes(tickangle=45)
    return fig


# def iny(n_clsick,TINY):
#     datos_iny = pd.read_csv("datasets/inyeccion_geo.csv", delimiter = ';')
#     name_campo=TINY
#     fig = make_subplots(
#         rows=1, cols=2,
#         specs=[[{"type": "scatter"}, {"type": "bar"}]],
#         subplot_titles=('Volúmenes de agua (bbl) - '+name_campo, "Total por año" ))
#     months=[]
#     for i in datos_iny.columns:
#         if '-' in i:
#             months.append(i)
#     del i
#     # name_campo='LA CIRA'
#     iny_df=datos_iny[datos_iny['CAMPO']==name_campo]

#     fig.add_trace(
#         go.Scatter(x=months,y=[float(np.array(iny_df[x])[0]) for x in months],name=name_campo,showlegend=False),
#         row=1, col=1
#     )
#     años=np.arange(2017,2022)
#     old=np.array([0,0,0,0,0])
#     for i in datos_iny['CAMPO']:
#         if i!='TOTAL':
#             campiny=datos_iny[datos_iny['CAMPO']==i]
#             new=[float(np.array(campiny[age])[0]) for age in años.astype(str)]
#             fig.add_trace(
#                 go.Bar(name=i, x=años, y=new+old,hovertemplate=['bbl:'+str(x) for x in new],showlegend=False),row=1, col=2)
#             old=new
#         else:
#             pass
#     del i
#     fig.update_layout(margin=dict(t=50,l=50,b=50,r=50),hoverlabel=dict(
#                         # bgcolor="white",
#                         font_size=12,
#                         font_family="Poppins"
#                     ),barmode='stack',
#                     # title_text="Inyección de agua para recobro mejorado en campos de hidrocarburos (ANH)", 
#                     font_family="Poppins")
#     fig.update_yaxes(tickvals=np.arange(0,300000000+1,50000000),row=2, col=2)
#     fig.update_xaxes(tickvals=años,row=2, col=2)
#     fig.update_xaxes(tickangle=45)
#     return fig

if __name__ == "__main__":
    app.run_server(debug=True)