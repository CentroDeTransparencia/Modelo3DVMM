import plotly.graph_objects as go
import pandas as pd

#Fallas geologicas 3d
fs=pd.read_csv('./datasets/new_surfaces.txt')

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