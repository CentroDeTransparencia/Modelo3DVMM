import pandas as pd
import plotly.graph_objects as go
import numpy as np
import skimage.io as sio
import math
import shapely
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString

#Función "cylinder" y "boundary circle" extraido de https://community.plotly.com/t/basic-3d-cylinders/27990/3
pd.options.mode.chained_assignment = None 
def cylinder(r, h,x0,y0,a=0, nt=600, nv=50):
    """
    Función para generar el arreglo numerico para el cilindro
    r=radio
    h=altura
    x0=Centro en x
    y0=Centro en y
    a=altura de tope (z)
    nt=npts eje x
    nv=npts eje z
    """
    theta = np.linspace(0, 2*np.pi, nt)
    v = np.linspace(a, a+h, nv )
    theta, v = np.meshgrid(theta, v)
    x = r*np.cos(theta)+x0
    y = r*np.sin(theta)+y0
    z = v
    return x, y, z

def boundary_circle(r, h,x0,y0, nt=600):
    """
    Función para generar el arreglo numerico del borde del cilindro
    r=radio del borde
    h=altura sobre el eje xy (z)
    nt=npts
    x0=centro en x
    y0=centro en y
    """
    theta = np.linspace(0, 2*np.pi, nt)
    x= r*np.cos(theta)+x0
    y = r*np.sin(theta)+y0
    z = h*np.ones(theta.shape)
    return x, y, z

#--

def volumen_semaforo(r1,a1,h1,x01,y01,opac,col_cyl,col_cir,name):
    """
    Función para generar cilindros basados en un arreglo previamente definido
    Variables iguales a la funcion "cylinder" y "boundary circle"
    """
    x1, y1, z1 = cylinder(r1, h1,x01,y01, a=a1)
    cyl1 = go.Surface(x=x1, y=y1, z=z1,
                    colorscale = col_cyl,
                    showscale=False,
                    opacity=opac,
                    name=name,
                    hovertemplate=name)
    xb_low, yb_low, zb_low = boundary_circle(r1, a1,x01,y01)
    xb_up, yb_up, zb_up = boundary_circle(r1, a1+h1,x01,y01)

    bcircles1 =go.Scatter3d(x = xb_low.tolist()+[None]+xb_up.tolist(),
                            y = yb_low.tolist()+[None]+yb_up.tolist(),
                            z = zb_low.tolist()+[None]+zb_up.tolist(),
                            mode ='lines',
                            line = dict(color=col_cir, width=2),
                            opacity =0.3, showlegend=False,
                            name=name,
                            hovertemplate=name)
    return cyl1,bcircles1

def vol_sus(x_pozo, y_pozo,h_pozo,nam,c,hort_pozo=0):
    """
    Función para generar trazas de pozos con volumenes de monitoreo según PPII
    Variables iguales a la funcion "volumen_semaforo"
    """
    r_ext = 2*(h_pozo+hort_pozo)+20000 #m
    ppii= go.Scatter3d(
    x=np.array(x_pozo),
    y=np.array(y_pozo),
    z=np.array(500),
    text=nam,
    textposition= 'top center',
    textfont=dict(
    family="Poppins",
    size=12,
    color="black"
    ),
    mode='markers+text',
    marker_symbol='diamond-open',
    name=nam,
    hovertemplate ="PPII",
    marker=dict(
    size=8,
    color=c
    ))

    r1=r_ext-20000

    #Volumen de suspension
    cyl1,bcircles1=volumen_semaforo(r1/(111.1*1000) ,0,-16000,
            x_pozo,y_pozo,0.5,
            ['red','red'],'red','Suspensión')
    #Volumen de monitoreo
    cyl2,bcircles2=volumen_semaforo(r_ext/(111.1*1000),0,-16000,
            x_pozo,y_pozo,0.7,
            ['green','orange'],'green','Monitoreo')
    #Volumen externo
    cyl3,bcircles3=volumen_semaforo(50000/(111.1*1000),0,-32000,
            x_pozo,y_pozo,0.3,
            ['aqua','aqua'],'blue','Externo')
            
    return ppii,cyl1,bcircles1,cyl2,bcircles2,cyl3,bcircles3

#Perfiles de superficie
def geologic_profile(x0,y0,x1,y1,url,name,colr,usecols,delimiter,decimal,res_x=0.01,res_y=0.01):
    """
    Función para generar perfiles de diversas superficies
    """
    df_geo=pd.read_csv(url,delimiter=delimiter,usecols=usecols,decimal=decimal)
    if usecols==['lon','lat','Z']:
        df_geo.rename(columns = {'lon':'X', 'lat':'Y'}, inplace = True)
    else:
        df_geo.columns = ['X', 'Y','Z']
    x=[x0,x1]
    y=[y0,y1]
    if x0!=x1:
        slope, intercept = np.polyfit(x,y,1)
        dist=np.sqrt(((x1-x0)**2)+(y1-y0)**2)
        x_lin=np.linspace(x0,x1,int(dist*100))
        y_lin=(slope*x_lin)+intercept
    else:
        slope, intercept = np.polyfit(y,x,1)
        dist=np.sqrt(((x1-x0)**2)+(y1-y0)**2)
        y_lin=np.linspace(y0,y1,int(dist*100))
        x_lin=(slope*y_lin)+intercept
    z,d=[],[]
    for xln,yln in zip(x_lin,y_lin):
            df_topo_1=df_geo[(df_geo['X']<=xln+res_x)&
                             (df_geo['X']>=xln-res_x)&
                             (df_geo['Y']>=yln-res_y)&
                             (df_geo['Y']<=yln+res_y)]
            dist_2=1
            forms=len(df_topo_1)
            if forms>0:
                for xt,yt,zt in zip(df_topo_1['X'],df_topo_1['Y'],df_topo_1['Z']):
                    d_prov=np.sqrt((xt-xln)**2+(yt-yln)**2)
                    if d_prov<dist_2:
                        dist_1=np.sqrt((xt-x0)**2+(yt-y0)**2)
                        dist_2=d_prov
                        z_p=zt
                if dist_2==1:
                    dist_1=np.nan
                    z_p=np.nan
            else:
                dist_1=np.nan
                z_p=np.nan
            z.append(z_p)
            d.append(dist_1)
    fig_1 = go.Scatter(x=d, y=z,
                    mode='lines',
                    name=name,
                    hovertext=name,
                    hoverinfo='text',
                    line=dict(color=colr, width=2))
    return fig_1

#Funcion para perfiles topograficos
def topo_profile(x0,x1,y0,y1,df_topo):
    """
    Función para generar perfil de la topografia
    """
    x=[x0,x1]
    y=[y0,y1]
    if x0!=x1:
        slope, intercept = np.polyfit(x,y,1)
        dist=np.sqrt(((x1-x0)**2)+(y1-y0)**2)
        x_lin=np.linspace(x0,x1,int(dist*100))
        y_lin=(slope*x_lin)+intercept
    else:
        slope, intercept = np.polyfit(y,x,1)
        dist=np.sqrt(((x1-x0)**2)+(y1-y0)**2)
        y_lin=np.linspace(y0,y1,int(dist*100))
        x_lin=(slope*y_lin)+intercept
    z=[]
    d=[]
    for xln,yln in zip(x_lin,y_lin):
        df_topo_1=df_topo[(df_topo[0]<xln+0.01)&(df_topo[0]>xln-0.01)&(df_topo[1]>yln-0.01)&(df_topo[1]<yln+0.01)]
        dist_2=10
        for xt,yt,zt in zip(df_topo_1[0],df_topo_1[1],df_topo_1[2]):
            d_prov=np.sqrt((xt-xln)**2+(yt-yln)**2)
            # print(d_prov)
            if d_prov<dist_2:
                dist_1=np.sqrt((xt-x0)**2+(yt-y0)**2)
                dist_2=d_prov
                z_p=zt
        z.append(z_p)
        d.append(dist_1)
    fig_1 = go.Scatter(x=d, y=z,
                mode='lines',
                name='Topografía',
                line=dict(color='black', width=2))
    return fig_1

#Imagen sismica
def img_3d(nam,url,x0,y0,x1,y1,z0,z1):
    """
    Función para generar plano de imagen en blanco y negro en 3d
    nam=Nombre de la traza
    url=Path
    x0,y0,x1,y1,z0,z1=Localización
    """
    image = sio.imread (url)
    zs,xys,_=image.shape
    zs,xys=int(zs),int(xys)
    yy = np.linspace(y0,y1, xys)
    zz = np.linspace(z1,z0, zs)
    yy, zz = np.meshgrid(yy, zz)
    x_data=list(np.linspace(x0,x1, xys))
    x_data=[x_data]*zs
    xx=np.concatenate(x_data).reshape(yy.shape)
    img = image[:,:, 1]
    ima_surface=go.Surface(name=str(nam),hovertemplate=str(nam),x=xx, y=yy, z=zz, surfacecolor= np.flipud(img), colorscale='greys', showscale=False)
    return ima_surface

#Plano de perfil de corte
def profile_plane(x0,y0,x1,y1):
    """
    Función para generar perfil 3D
    """
    yy = np.linspace(y0,y1, 3)
    zz = np.linspace(-32000,10000, 3)
    yy, zz = np.meshgrid(yy, zz)
    x_data=list(np.linspace(x0,x1, 3))
    x_data=[x_data]*3
    xx=np.concatenate(x_data).reshape(yy.shape)
    ima_surface=go.Surface(x=xx, y=yy, z=zz, colorscale=['red','red'], showscale=False,opacity=0.5,name='Perfil',hoverinfo='none')
    return ima_surface


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def profile(x1,x2,y1,y2,df_sismos_1,types,):
    """
    Función para generar df con los sismos y/o pozos adentro de un perfil de grosor 0.1°
    """
    x=[x1,x2]
    y=[y1,y2]
    if x1==x2:
        dist=np.sqrt(((x2-x1)**2)+(y2-y1)**2)
    else:
        dist=np.sqrt(((x2-x1)**2)+(y2-y1)**2)
    dx,dy=(x1-x2,y1-y2)
    try:
        rot=np.arctan(dx/dy)
    except:
        rot=0
    o1,o2=((x1,y1),(x2,y2))
    p1_s=rotate(o1, (x1+0.1,y1), -rot)
    p1_i=rotate(o1, (x1-0.1,y1), -rot)
    p2_s=rotate(o2, (x2+0.1,y2), -rot)
    p2_i=rotate(o2, (x2-0.1,y2), -rot)
    polygon = Polygon([p1_s, p1_i, p2_i, p2_s])
    if y1==y2:
        polygon = Polygon([(x1,y1+0.1), (x1,y1-0.1), (x2,y1+0.1), (x2,y1+0.1)])
    elif x1==x2:
        polygon = Polygon([(x1+0.1,y1), (x1-0.1,y1), (x1+0.1,y2), (x1-0.1,y2)])
    else:
        pass
    id_ls=[]
    if types=='sismos':
        for x,y,id in zip(df_sismos_1[ 'LONGITUD (°)'],df_sismos_1[ 'LATITUD (°)'],df_sismos_1['Unnamed: 0']):
            if polygon.contains(Point(x,y)):
                id_ls.append(id)
        df_profile=df_sismos_1[np.isin(df_sismos_1['Unnamed: 0'], id_ls)]
        df_profile['DIST']=np.sqrt(((x1-df_profile['LONGITUD (°)'])**2)+((y1-df_profile['LATITUD (°)'])**2)) 
        return df_profile,dist
    elif types=='pozos':
        for x,y,id in zip(df_sismos_1[ 'lon'],df_sismos_1[ 'lat'],df_sismos_1.index):
            if polygon.contains(Point(x,y)):
                id_ls.append(id)
        df_profile=df_sismos_1[np.isin(df_sismos_1.index, id_ls)]
        df_profile['DIST']=np.sqrt(((x1-df_profile['lon'])**2)+((y1-df_profile['lat'])**2)) 
        return df_profile,dist

#Función para crear los perfiles de los semaforos
def semaforo_profile(x1,x2,y1,y2,df_pozos):
    """
    Función para crear los perfiles de los semaforos
    """
    df_pozos=df_pozos[0:4]
    sem_ls=[]
    for x,y,prof,name in zip(df_pozos['lon'],df_pozos['lat'],df_pozos['TVD'],df_pozos['name']):
        p = Point(x,y)
        for r,col,prof_new,name_new,opa in zip(
        [(2*prof)/1000,((2*prof)/1000)+20,50],
        ['red','yellow','blue'],
        [16000,16000,32000],
        ['Suspensión','Monitoreo','Externo'],
        ['rgba(255,17,0,0.8)','rgba(205,255,0,0.5)','rgba(9,0,255,0.2)']):
            r=r/111.1
            c = p.buffer(r).boundary
            l = LineString([(x1,y1), (x2, y2)])
            i = c.intersection(l)
            if type(i)==shapely.geometry.multipoint.MultiPoint:
                # print(i)
                lon_1,lat_1=i.geoms[0].coords[0]
                lon_2,lat_2=i.geoms[1].coords[0]
                dist_1=np.sqrt(((x1-lon_1)**2)+(y1-lat_1)**2)
                dist_2=np.sqrt(((x1-lon_2)**2)+(y1-lat_2)**2)
                # for dist,num in zip([dist_1,dist_2],['1.','2.']):
                sem=go.Scatter(x=[dist_1,dist_1,dist_2,dist_2]*2,
                                y=[69,-prof_new,-prof_new,69],
                                fill='tozeroy',
                            #    mode='lines',
                                legendgroup=name,  # this can be any string, not just "group"
                                legendgrouptitle=dict(text=str(name)),
                                hovertemplate=str(name)+' | '+name_new,
                                name=str(name)+' | '+name_new,
                                visible='legendonly',
                                fillcolor=opa,
                                line=dict(color=col, width=2),
                                # opacity=opa
                                )
                sem_ls.append(sem)

            else:
                pass
    return sem_ls

def surface_3d(url,color_min,color_max,name_geo,kind):
    """
    Función para crear las superficies en 3D
    """
    if kind==1:
        df_geo=pd.read_csv(url,delimiter=';',usecols=[1,2,3],decimal=',')
        df_geo.columns = ['Z', 'X', 'Y']
        mesh_geo=df_geo.pivot(index='Y', columns='X',values='Z')
    elif kind==2:
        df_geo=pd.read_csv(url,delimiter=',')
        mesh_geo=df_geo.pivot(index='lat', columns='lon',values='Z')
    
    geology=go.Surface(z=mesh_geo.values,
                        showscale=False, 
                        x=mesh_geo.columns, 
                        y=mesh_geo.index,
                        showlegend=False,
                        opacity=0.9,
                        colorscale=[color_max,color_min],
                        name=name_geo,
                        hovertemplate=name_geo,
                        hoverinfo='none',
                        lighting=dict(ambient=0.3,diffuse=0.5))
    return geology


def geology_super(df_geo,color,name_geo,text,TOPO):
    """
    Función para crear la geología superficial
    """
    df_geo=df_geo.drop_duplicates(subset=['X','Y'])
    mesh_geo=df_geo.pivot(index='Y', columns='X',values='Z')
    geology=go.Surface(z=mesh_geo.values+5,showscale=False, x=mesh_geo.columns, y=mesh_geo.index,showlegend=False,opacity=TOPO,colorscale=[color,color],name=name_geo,
                                hovertemplate=text,lighting=dict(ambient=0.2))
    return geology



def orientation(x0,y0,x1,y1):
    """
    Definir la orientación del perfil
    """
    if x0==x1:
        if y0<y1:
            p1='S';p2='N'
        else:
            p1='N';p2='S'
    elif y0==y1:
        if x0<x1:
            p1='W';p2='E'
        else:
            p1='E';p2='W'
    else:
        alpha=np.arctan((np.abs(y0-y1))/(np.abs(x0-x1)))
        alpha=np.degrees(alpha)
        if x0<x1 and y0<y1:
            if alpha==45:
                p1='SW';p2='NE'
            elif alpha<45:
                p1='WSW';p2='ENE'
            else:
                p1='SSW';p2='NNE'
        if x0>x1 and y0>y1:
            if alpha==45:
                p1='NE';p2='SW'
            elif alpha<45:
                p1='ENE';p2='WSW'
            else:
                p1='NNE';p2='SSW'           
        if x0>x1 and y0<y1:
            if alpha==45:
                p1='SE';p2='NW'
            elif alpha<45:
                p1='ESE';p2='WNW'
            else:
                p1='SSE';p2='NNW'    
        if x0<x1 and y0>y1:
            if alpha==45:
                p1='NW';p2='SE'
            elif alpha<45:
                p1='WNW';p2='ESE'
            else:
                p1='NNW';p2='SSE'  
            
    return p1,p2

def text_scatter(SEISMO,df_sismos_1):
    """
    Definir el texto del semaforo
    """
    ls_txt=[]
    try:
        if np.isin('LOC', SEISMO):
            ls_txt.append('Longitud:'+df_sismos_1['LONGITUD (°)'].astype(str)+'°'+'<br>'
                            'Latitud:'+df_sismos_1['LATITUD (°)'].astype(str)+'°'+'<br>'+
                            'Profundidad :'+df_sismos_1['PROF. (m)'].astype(str)+'m <br>')
        if np.isin('MAG', SEISMO):
            ls_txt.append('Fecha :'+df_sismos_1['FECHA - HORA UTC'].astype(str)+'<br>')
        if np.isin('FEC', SEISMO):
            ls_txt.append('Magnitud:'+df_sismos_1['MAGNITUD'].astype(str)+'<br>'+
            'Tipo de magnitud:'+df_sismos_1['TIPO MAGNITUD']+'<br>')
        if np.isin('RMS', SEISMO):
            ls_txt.append('RMS (Segundos):'+df_sismos_1['RMS (Seg)'].astype(str)+'s <br>')
        if np.isin('ERR', SEISMO):
            ls_txt.append('Error en la latitud (m):'+df_sismos_1['ERROR LATITUD (Km)'].apply(lambda x:str(x*1000))+'m <br>'+
            'Error en la longitud (m):'+df_sismos_1['ERROR LONGITUD (Km)'].apply(lambda x:str(x*1000))+'m <br>'+
            'Error en la profundidad (m):'+df_sismos_1['ERROR PROFUNDIDAD (Km)'].apply(lambda x:str(x*1000))+'m <br>')
        if len(ls_txt)==0:
            text=' '
        else:
            text=''
            for i in ls_txt:
                text=text+i
    except:
        text='No hay sismos'
    return text

def Color_Integridad(x):
    """
    Definir el color de integridad
    """
    if x=='Baja':
        return 'green'
    elif x=='Media':
        return 'yellow'
    else:
        return 'red'

def az2pyt(az):
    """
    Pazar de azymut a pythagorean projection para WSM
    """
    if az<=90:
        return az-90
    elif az<=180:
        return 270+(180-az)
    elif az<=270:
        return 180+(270-az)
    else:
        return 90+(360-az)