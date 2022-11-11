import pandas as pd
import plotly.graph_objects as go
import numpy as np
from geoseismo import *
#Area del estudio
los=-73
loi=-74.4
lai=6.5
las=9

#Topografía
#Se cargan los datos de elevacion estos fueron descargados en https://portal.opentopography.org/datasets
# Global Bathymetry and Topography at 15 Arc Sec: SRTM15+ V2.1  
df_topo   =pd.read_csv('./datasets/topo_src_15.csv')
mesh_topo = (df_topo.pivot(index='1', columns='0',values='2'))
z_topo,x_topo,y_topo=mesh_topo.values,mesh_topo.columns,mesh_topo.index


topog=go.Surface(z=z_topo,showscale=False, x=x_topo, y=y_topo,colorscale=['black','black'],lighting=dict(ambient=0.3,diffuse=0.5),
                    showlegend=False,opacity=1,name='Topografía',hoverinfo='none')
del mesh_topo,z_topo,x_topo,y_topo
#Sismos
#Base de datos de sismos convertidos a csv desde http://bdrsnc.sgc.gov.co/paginas1/catalogo/Consulta_Valle_Medio/valle_medio.php
df_sismos=pd.read_csv('./datasets/reporte_LBG.csv')

#Pozos
df_pozos=pd.read_csv('./datasets/pozos.csv')
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
    arrayminus=df_pozos['WELL_TVD'].values,             
    color='black',   # choose a colorscale
    symmetric=False,
    width=0.01,
    visible=True),
    marker=dict(
        size=1.5,
        color='black'
    )
)

#Inyeccion de H20
iny=pd.read_csv('./datasets/inyeccion_geo.csv',delimiter=';',decimal=',')
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
kale_tray=pd.read_csv('./datasets\Kale-1H_1.csv')
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

plat_tray=pd.read_csv('./datasets\Platero-1H_1.csv')

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
df_sta_vmm=pd.read_csv('./datasets/VMM_STA.csv',delimiter=';',decimal=',')
df_sta_lom=pd.read_csv('./datasets/LOMA_STA.csv',delimiter=';',decimal=',')

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
df_geos=pd.read_csv('./datasets/geo_unit_sup.csv')

#Rios
rivers=pd.read_csv('./datasets/drenajes.csv')
rivers_ls=[]
for i in rivers['LINE_ID'].unique():
    riv1=rivers[rivers['LINE_ID']==i]
    rivers_ls.append(go.Scatter3d(x=riv1['X'], y=riv1['Y'], z=riv1['Z'],
                                    hovertemplate=str(np.array(riv1['NOMBRE_GEO'])[0]),
                                    mode='lines',
                                    name='Ríos',line=dict(color='aqua',width=4),showlegend=False))
del rivers,i

#Integridad Pozos Kale
critic=pd.read_csv('./datasets/criticidad_Kale.csv',decimal=',')

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
df_rezumaderos=pd.read_csv('./datasets\REZUMADEROS_WGS84_SIM.txt',decimal=',',delimiter=';')
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
ol=pd.read_csv('./datasets/topes_olini.csv')
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
st=pd.read_csv('./datasets/wsm2016.csv')

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

del st,i,st_1

#Poblaciones
df_poblaciones=pd.read_csv('./datasets/poblaciones.csv')
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
del df_poblaciones,un

#Carreteras
roads=pd.read_csv('./datasets\Via_WGS84_SIM.txt')
roads  =roads[(roads['LATITUD']>lai)&(roads['LATITUD']<las)&(roads['LONGITUD']>loi)&(roads['LONGITUD']<los)]
roads_ls=[]
for i in roads['GLOBALID'].unique():
    f=roads[roads['GLOBALID']==i]
    roads_ls.append(go.Scatter3d(x=f['LONGITUD'], y=f['LATITUD'], z=f['ELEVACION'],
    hovertemplate=str(i),mode='lines',name='Via',line=dict(color='yellow',width=2),showlegend=False),)

del roads,i

fallas=pd.read_csv('./datasets/fallas.csv')
fallas_ls=[]
for i in fallas['LINE_ID'].unique():
    f=fallas[fallas['LINE_ID']==i]
    try:
        nom=np.array(f['NombreFall'])[0]
    except:
        nom='_'
    try:
        tip=np.array(f['Tipo'])[0]
    except:
        tip='_'
    fallas_ls.append(go.Scatter3d(x=f['X'], y=f['Y'], z=f['Z'],
                    hovertemplate=nom,
                    mode='lines',
                    name=tip,line=dict(color='red',width=4),showlegend=False),)
del fallas,nom,tip,i

campet=pd.read_csv('./datasets/campos.csv')
campet_ls=[]
for i in campet['LINE_ID'].unique():
    f=campet[campet['LINE_ID']==i]
    nom='Compañia:'+np.array(f['Compañia'])[0]+'<br>Estado:'+np.array(f['Estado'])[0]+'<br>Información:'+str(np.array(f['INFO'])[0])
    try:
        tip='Campo petrolífero '+np.array(f['Campo'])[0]
    except:
        tip='_'
    campet_ls.append(go.Scatter3d(x=f['X'], y=f['Y'], z=f['Z'],
                    hovertemplate=nom,
                    mode='lines',
                    name=tip,line=dict(color='black',width=3),showlegend=False),)
    
del campet,i,tip,nom

#Hidrogeología
hidro_well=pd.read_csv('./datasets\inv_hidro.csv')
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
hw=pd.read_csv('./datasets/pozos_adquisicion_hidro.csv')

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

kalei,kicyl1,kibcircles1,kicyl2,kibcircles2,kicyl3,kibcircles3=vol_sus(-73.8566, 7.36551,3902,'Kalé - Investigación','blue',1651.9414772880211)
kaley,kycyl1,kybcircles1,kycyl2,kybcircles2,kycyl3,kybcircles3=vol_sus(-73.8571014, 7.3647799,2618.232,'Kalé - Inyector','aqua')
plai,picyl1,pibcircles1,picyl2,pibcircles2,picyl3,pibcircles3=vol_sus(-73.89389, 7.2572498,3227.8,'Platero - Investigación','red',1616.6333446235456)
play,pycyl1,pybcircles1,pycyl2,pybcircles2,pycyl3,pybcircles3=vol_sus(-73.8944016, 7.25667,2325.6,'Platero - Inyector','orange')

kalec,_,_,_,_,_,_=vol_sus(-73.8570023, 7.3647499,2325.6,'Kalé - Captador','orange')
plac,_,_,_,_,_,_=vol_sus(-73.8943024, 7.2566800,2325.6,'Platero - Captador','gold')

#Fallas geologicas 3d #More time +10 sec
# fs=pd.read_csv('datasets/new_surfaces.txt')

# g1,g2,g3=[],[],[]
# for n,ls in zip(fs['clas'].unique(),[g1,g2,g3]):
#         fs1=fs[fs['clas']==n]
#         for i in fs1['name'].unique():
#             fs2=fs1[fs['name']==i]
#             fs2=fs2.drop_duplicates()
#             mesh_geo=fs2.pivot(index='Y', columns='X',values='Z')
#             fault_surface=go.Surface(z=mesh_geo.values*-1,showscale=False, x=mesh_geo.columns, 
#                     y=mesh_geo.index,showlegend=False,opacity=0.9,colorscale=['red','pink'],hovertemplate=i,name='Falla geológica')
#             ls.append(fault_surface)
# del n,ls,fs
