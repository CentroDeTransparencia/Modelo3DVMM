from pydoc import classname
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
# from plotly.subplots import make_subplots
import io
from flask import Flask
# import os
from geoseismo import *
import warnings
from graficas.iny_bar_total import fig as iny_bar
# from graficas.iny_bar_total import iny
from M3DVMM.general import *

warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None 

#Geologia superficial
df_geos=pd.read_csv('datasets/geo_unit_sup.csv')

#Colores geologia
df_colors_geo=pd.read_csv('datasets/UN_CRN_COLORS.csv',index_col=None)

#Explicacion modelo
exp=io.open("datasets\Explicacion_modelo3d.txt", mode="r", encoding="utf-8")
ls_k=[html.H2('¿Cómo funciona el modelo tridimensional del Valle Medio del Magdalena?', className="card-text")]
for i in exp:
    ls_k.append(html.H6(i, className="card-text"))

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
     dbc.Button('Abrir panel de control', color='info', id='btn_sidebar', size="lg"), 
     className = 'button_sidebar'
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
                    #  dbc.Button(html.I(), color='primary', id='btn_sidebar', size="lg"),
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
        # html.Button("¿Cómo funciona?", id="function_but_xl",  className="footerButtons", n_clicks=0),
        # html.Button("¿Semáforo sísmico?", id="semaforo_but_xl", className="footerButtons", n_clicks=0),
        # html.Button("Referencias", id="references_but_xl", className="footerButtons", n_clicks=0)
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
            iny=pd.read_csv(r'datasets\inyeccion_geo.csv',delimiter=';',decimal=',')
            iny=iny[:-1]
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
            from M3DVMM.seismics import sismica_1
            fig.add_trace(sismica_1)
        if np.isin('SEIS_2', PETRO):
            from M3DVMM.seismics import sismica_2
            fig.add_trace(sismica_2)
        if np.isin('SEIS_3', PETRO):
            from M3DVMM.seismics import sismica_3
            fig.add_trace(sismica_3)
        if np.isin('SEIS_4', PETRO):
            from M3DVMM.seismics import sismica_4
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
            from M3DVMM.geosurfaces import Real
            Real.opacity=TGREAL
            fig.add_trace(Real)
            grealo={'display': 'block'}
        else:
            grealo={'display': 'none'}

        if np.isin('COL', GEOL):
            from M3DVMM.geosurfaces import Colorado
            Colorado.opacity=TCOLORADO
            fig.add_trace(Colorado)
            coloradoo={'display': 'block'}
        else:
            coloradoo={'display': 'none'}       
        if np.isin('MUG', GEOL):
            from M3DVMM.geosurfaces import Mugrosa
            Mugrosa.opacity=TMUGROSA
            fig.add_trace(Mugrosa)
            mugrosao={'display': 'block'}
        else:
            mugrosao={'display': 'none'}
        if np.isin('CHO', GEOL):
            from M3DVMM.geosurfaces import Chorros
            Chorros.opacity=TCHORROS
            fig.add_trace(Chorros)
            chorroso={'display': 'block'}
        else:
            chorroso={'display': 'none'}
        if np.isin('EOC', GEOL):
            from M3DVMM.geosurfaces import Eoceno
            Eoceno.opacity=TEOCMED
            fig.add_trace(Eoceno)
            eocmedo={'display': 'block'}
        else:
            eocmedo={'display': 'none'}
#PAJA
        if np.isin('PAJA', GEOL):
            from M3DVMM.geosurfaces import paja
            paja.opacity=TPAJA
            fig.add_trace(paja)
            pajao={'display': 'block'}
        else:
            pajao={'display': 'none'}
        #Salada
        if np.isin('SALADA', GEOL):
            from M3DVMM.geosurfaces import salada
            salada.opacity=TSALADA
            fig.add_trace(salada)
            salado={'display': 'block'}
        else:
            salado={'display': 'none'}
        #Simiti
        if np.isin('SIMITI', GEOL):
            from M3DVMM.geosurfaces import simiti
            simiti.opacity=TSIMITI
            fig.add_trace(simiti)
            simitio={'display': 'block'}
        else:
            simitio={'display': 'none'}
        #Galembo
        if np.isin('GALEMBO', GEOL):
            from M3DVMM.geosurfaces import galembo
            galembo.opacity=TGALEMBO
            fig.add_trace(galembo)
            galemboo={'display': 'block'}
        else:
            galemboo ={'display': 'none'}
        #CiraShale
        if np.isin('CIRASHALE', GEOL):
            from M3DVMM.geosurfaces import ciraShale
            ciraShale.opacity=TCIRASHALE
            fig.add_trace(ciraShale)
            ciraShaleo={'display': 'block'}
        else:
            ciraShaleo ={'display': 'none'}
        #Bagre
        if np.isin('BAGRE', GEOL):
            from M3DVMM.geosurfaces import bagre
            bagre.opacity=TBAGRE
            fig.add_trace(bagre)
            bagreo={'display': 'block'}
        else:
            bagreo ={'display': 'none'}
        #Chontorales
        if np.isin('CHONTORALES', GEOL):
            from M3DVMM.geosurfaces import chontorales
            chontorales.opacity=TCHONTORALES
            fig.add_trace(chontorales)
            chontoraleso={'display': 'block'}
        else:
            chontoraleso ={'display': 'none'}
        #Coloradoh
        if np.isin('COLORADOH', GEOL):
            from M3DVMM.geosurfaces import colorado
            colorado.opacity=TCOLORADOH
            fig.add_trace(colorado)
            coloradoho={'display': 'block'}
        else:
            coloradoho ={'display': 'none'}
        #Enrejado
        if np.isin('ENREJADO', GEOL):
            from M3DVMM.geosurfaces import enrejado
            enrejado.opacity=TENREJADO
            fig.add_trace(enrejado)
            enrejadoo={'display': 'block'}
        else:
            enrejadoo ={'display': 'none'}
        #Esmeraldas
        if np.isin('ESMERALDAS', GEOL):
            from M3DVMM.geosurfaces import esmeraldas
            esmeraldas.opacity=TESMERALDAS
            fig.add_trace(esmeraldas)
            esmeraldaso={'display': 'block'}
        else:
            esmeraldaso ={'display': 'none'}
        #Hiel
        if np.isin('HIEL', GEOL):
            from M3DVMM.geosurfaces import hiel
            hiel.opacity=THIEL
            fig.add_trace(hiel)
            hielo={'display': 'block'}
        else:
            hielo ={'display': 'none'}
        #Lluvia
        if np.isin('LLUVIA', GEOL):
            from M3DVMM.geosurfaces import lluvia
            lluvia.opacity=TLLUVIA
            fig.add_trace(lluvia)
            lluviao={'display': 'block'}
        else:
            lluviao ={'display': 'none'}
        #Galembo
        if np.isin('MUGROSAH', GEOL):
            from M3DVMM.geosurfaces import mugros
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
            from M3DVMM.fallas import g2
            fig.add_traces(g2)
        if np.isin('g2', GEOL):
            from M3DVMM.fallas import g1
            fig.add_traces(g1)
        if np.isin('g3', GEOL):
            from M3DVMM.fallas import g3
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
     dash.dependencies.Output('btn_sidebar','className'),
     dash.dependencies.Output('btn_sidebar', 'children')
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
            text_btn = ' Abrir panel de control'           
        if n_clicks == 'hidden':
            sidebar_classname = 'sidebar'
            content_classname = 'model_graph'
            c_clicks = 'show'
            btn_sidebar_className = 'bi bi-arrow-bar-left'
            text_btn = ' Cerrar panel de control' 
    else:
        sidebar_classname = 'sidebar_hidden'
        content_classname = 'content_sidebar_hidden'
        c_clicks = 'hidden'
        btn_sidebar_className = 'bi bi-arrow-bar-right' 
        text_btn = ' Abrir panel de control'
    return sidebar_classname, content_classname, c_clicks, btn_sidebar_className, text_btn
    
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
                        margin=dict(t=50,l=50,b=50,r=50), showlegend = True)
    fig2.update_layout(legend=dict(
        orientation="h",
        #yanchor="bottom",
        y=-0.2,
        #xanchor="right",
        x=0
    ))
    fig2.update_layout(autosize = True, height=600)
    # fig2.update_layout(legend_x=0, legend_y=-1)
    return fig2

@app.callback(
     dash.dependencies.Output(component_id='Iny_graph', component_property='figure'),
    [dash.dependencies.Input('submit-val', 'n_clicks'),
    dash.dependencies.State(component_id='TINY', component_property='value')])

def iny(n_clsick,TINY):
    datos_iny = pd.read_csv("datasets/inyeccion_geo.csv", delimiter = ';')
    #'Volúmenes de agua (bbl) - '+name_campo
    name_campo=TINY
    fig = go.Figure()
    months=[]
    for i in datos_iny.columns:
        if '-' in i:
            months.append(i)
    del i
    # name_campo='LA CIRA'
    iny_df=datos_iny[datos_iny['CAMPO']==name_campo]

    fig.add_trace(
        go.Scatter(x=months,y=[float(np.array(iny_df[x])[0]) for x in months],name=name_campo,showlegend=False)
    )
    años=np.arange(2017,2022)
    old=np.array([0,0,0,0,0])
    fig.update_layout(margin=dict(t=50,l=50,b=50,r=50)
                      ,hoverlabel=dict(
                        # bgcolor="white",
                        font_size=12,
                        font_family="Poppins"),
                    title_text='Volúmenes de agua (bbl) - '+name_campo,
                    title_x = 0.5,
                    font_family="Poppins")
    fig.update_xaxes(tickangle=45)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)