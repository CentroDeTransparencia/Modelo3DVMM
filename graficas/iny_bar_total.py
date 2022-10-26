import pandas as pd
import numpy as np
import plotly.graph_objects as go

datos_iny = pd.read_csv("./datasets/inyeccion_geo.csv", delimiter = ';')

fig = go.Figure()

años=np.arange(2017,2022)
old=np.array([0,0,0,0,0])

for i in datos_iny['CAMPO']:
    if i!='TOTAL':
        campiny=datos_iny[datos_iny['CAMPO']==i]
        new=[float(np.array(campiny[age])[0]) for age in años.astype(str)]
        fig.add_trace(
            go.Bar(name=i, x=años, y=new+old,hovertemplate=['bbl:'+str(x) for x in new],showlegend=False))
        old=new
    else:
        pass
    
fig.update_layout(margin=dict(t=50,l=50,b=50,r=50),hoverlabel=dict(
                        # bgcolor="white",
                        font_size=12,
                        font_family="Poppins"
                    ),barmode='stack',
                    title_text="Total por año",
                    title_x = 0.5, 
                    font_family="Poppins")
  
