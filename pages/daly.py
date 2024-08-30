import dash
from dash import html, dcc, callback, Input, Output, dash_table,ctx
import dash_bootstrap_components as dbc
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from scipy import ndimage
from shapely.wkt import loads
import matplotlib.pylab as pylab
import warnings
import libpysal as ps

import plotly.express as px
import dash_loading_spinners as dls
import pandas as pd
from sidebar2 import *
#dash.register_page(__name__)
dash.register_page(
    __name__,
    path='/daly',
    title='DALYs Analytics Dashboard',
    name='DALYs Analytics Dashboard'
)
from DB_Man import *
GPD_MAP = gpd.GeoDataFrame.from_file("Map/Trat/Tambol/Trat.shx", encoding = 'utf-8')
GPD_MAP['geo_index'] = GPD_MAP.index
dimension_dict = {'level': 'ADM1_TH'}

PAGE_SIZE=20


content = html.Div(id='page-content',children=[
            dcc.Store(id = "BOD_AreaLevel"),
            dcc.Store(id = "BOD_AreaName"),
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1('Burden of Diseases',className=' text-white text-center'),
                    ],className='p-3 bg-info rounded-3 border-1 ')
                ]),
				dbc.Row([
					dbc.Col([
                            html.P("Select data level:"),
                            dcc.RadioItems(
                                id='BOD_SelLevel', 
                                options=["Province","District", "Subdistrict"],
                                value="Province",
                                inline=True
                            ),
                            dcc.Graph(id="BOD_graph"),
                            html.Br(),
                            dcc.Graph(id="BOD_BarChart"),
							],className='p-2 bg-light rounded-3',width=5
					        ),
    
					dbc.Col([
                        
						dbc.Row([
                            html.H2("Diseases table:"),
							html.Div("",id='BOD_LevelDetail')
						    ]),
                        dbc.Row([
							    dash_table.DataTable(id='BOD_DiseasesTable',
                                columns=[{'name': 'CODE', 'id': 'CODE',"selectable": True},
                                        {'name': 'Disease', 'id': 'Disease',"selectable": True},
                                        {'name': 'N', 'id': 'N',"selectable": True}],
                                    page_current=0,
                                    page_size=PAGE_SIZE,
                                    page_action='custom'
                                )
						    ]),
                        dbc.Row([
                            dbc.Alert(id='BOD_message_under_diseases')
                        ]),
                        dbc.Row([
							html.H2("Area comparison table:"),
                            dash_table.DataTable(id='BOD_AreaTable',
                                    sort_action="native",
                                    sort_mode="multi",
                                ),
							html.Div("",id='divBOD_AreaTable')
						    ]),
                        dbc.Row([
                            
							html.Div("",id='BOD_AreaInformation')
						    ],className='p-3  rounded-3 border-0'),
					    ],className='p-2 bg-light rounded-3  border-0',width = 7),
			        ],className='p-3  rounded-3 border-0'),
                    
                html.Hr(),
                dbc.Row([
					dbc.Col(children=[
                            html.H3("AI recommended policy recommendationssss:"),
                            html.P("--")                    
							],className='p-3 bg-info text-white rounded-3')
                    ])
	        ], fluid = True, style= {"marginTop":"30px","marginLeft":"30px"})
        ],style=CONTENT_STYLE)

layout = html.Div([sidebar,content])


@callback(
    Output("BOD_AreaTable", "selected_cells"),
    Output("BOD_AreaTable", "active_cell"),
    Input('BOD_AreaTable', 'active_cell')
)
def ClearAreaClick(ClickData):
    return [],None
@callback(
    Output("BOD_LevelDetail", "children"),
    Output("BOD_DiseasesTable","data"),
    Output("BOD_AreaTable","data"), 
    Output("BOD_BarChart", "figure"),
    Output('BOD_message_under_diseases', 'children'),
    Output("BOD_AreaInformation","children"),
    Output("BOD_AreaName","data"),
    Output("BOD_AreaTable", "style_data_conditional"),
    Output("BOD_DiseasesTable", "style_data_conditional"),
    Output('BOD_DiseasesTable', 'page_count'),
    Output("BOD_DiseasesTable", "selected_cells"),
    Output("BOD_DiseasesTable", "active_cell"),
    Output('BOD_DiseasesTable', "page_current"),
    Output("BOD_graph", "figure"),
    Input("BOD_graph","clickData"),
    Input('BOD_DiseasesTable', "page_current"),
    Input('BOD_DiseasesTable', "page_size"),
    Input('BOD_DiseasesTable', 'active_cell'),
    Input("BOD_AreaLevel", "data"),
    Input("ChooseProvince","value"),
    Input("BOD_SelLevel", "value"),
    Input("BOD_AreaName","data")
)
def UpdateAllWindows(clickData,page_current,page_size,active_cell,BOD_AreaLevel,ProvValue,BOD_SelLevel,BOD_AreaName):
    global df
    global DiseaseDf
    global DiseaseDf_Table
    global AreaDf
    global AreaDf_Table
    global BOD_Bargraph
    GrpValue=dimension_dict['level']
    if(BOD_SelLevel=='District'):
        #print("Coming here")
        grp='ADM2_TH'
    elif(BOD_SelLevel=='Subdistrict'):
        grp='ADM3_TH'
    else:
        grp='ADM1_TH'
    dimension_dict['level']=grp
    GrpValue=grp
    HighLightArea = dash.no_update
    HighLightDisease = dash.no_update
    Selected_Cell_Cmd=dash.no_update
    Selected_Cell_Value=dash.no_update
    ClickDisease = []
    button_clicked = ctx.triggered_id
    dimension_dict['level']=BOD_AreaLevel
    #print("WHAT IS CLICKED",button_clicked,"GROUP LEVEL=",GrpValue,"Sel level=",BOD_SelLevel,"PAGE CURRENT UP MOST=",page_current)
    MaxPages=5
    AreaText=''
    BOD_Map=dash.no_update
    RetText='Initial data'
    
    if(button_clicked=='BOD_graph'):
        Selected_Cell_Cmd=[]
        Selected_Cell_Value=None
        if (clickData is not None):
            #print("Map clicked!")
            IndexLocation=clickData['points'][0]['location']
            TambonText=GPD_MAP[GPD_MAP.index==IndexLocation][GrpValue].item()
            dimension_dict['Name']=TambonText
            BOD_AreaName=TambonText
            if (GrpValue=='ADM2_TH'):
                Pos=0
                DiseaseDf=BOD_df[BOD_df['ADM2_TH']==BOD_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Disease_ROW=0
                RetText=f'District name: {BOD_AreaName}'
                #Pos=1
                #print(DiseaseDf.head(10))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                #print("+++++++++++Code=",DiseaseDf.iloc[Pos]['CODE'])
                AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                #print("AREA DF=")
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==BOD_AreaName].index.values[0]
                #print(AreaDf);print("AREA Name=",BOD_AreaName)#print("AREA index=",AreaDf.index) #print("AREA Pos=",ADM2_TH_ROW)
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                #print("Disease row=",Disease_ROW)
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
                BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics comparison among districts.")
                BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
            elif(GrpValue=='ADM3_TH'):
                RetText=f'District name: {BOD_AreaName}'
                Pos=0
                DiseaseDf=BOD_df[BOD_df['ADM3_TH']==BOD_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Disease_ROW=0
                #print(DiseaseDf.head(10))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)                
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM3_TH']==BOD_AreaName].index.values[0]
                ADM3_TH_ROW=0
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
                BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics comparison among districts.")
                BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
                BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
                BOD_MapData['N']=BOD_MapData['N'].fillna(0)
                BOD_Map= px.choropleth(BOD_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','ADM3_TH','N'],
                        projection="mercator")
                BOD_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
                )
                dimension_dict['level'] = grp                                                                                                             
                BOD_Map.update_geos(fitbounds="locations", visible=False)
            else:
                #print("Whole map clicked")
                RetText=f'Province name: {TambonText}'
                RetText='Waiting for area selection - Whole map clicked'
                #DiseaseDf=BOD_df[BOD_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                ResText='Result text from whole map'
                #print(".................INITIAL MAP...........",BOD_AreaName)
                BOD_AreaName='ตราด'
                page_current=0
                RetText='Waiting for area selection-Area level click Province'
                DiseaseDf=BOD_df[BOD_df['ADM1_TH']==BOD_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf=BOD_df[BOD_df['ADM1_TH']==BOD_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                BOD_MapData['N']=BOD_MapData['N'].fillna(0)
                BOD_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics of province")
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
                HighLightDisease = []
                HighLightArea = []
                BOD_Map= px.choropleth(BOD_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        projection="mercator")
                dimension_dict['level'] = grp  
                                                                                                                           
                BOD_Map.update_geos(fitbounds="locations", visible=False)
                #print("End of Re-INITIAL")
    elif(button_clicked=='BOD_AreaLevel') | (button_clicked=='BOD_SelLevel'):   
        #print("AREA LEVEL CLICKED",GrpValue)
        Selected_Cell_Cmd=[]
        Selected_Cell_Value=None
        page_current=0
        if (GrpValue=='ADM2_TH'):
            Pos=0
            BOD_AreaName=BOD_InitialDistrict
            DiseaseDf=BOD_df[BOD_df['ADM2_TH']==BOD_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            Disease_ROW=0
            RetText=f'District name: {BOD_AreaName}'
            print(DiseaseDf.head(10))
            ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
            #print("+++++++++++Code=",DiseaseDf.iloc[Pos]['CODE'])
            AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==BOD_AreaName].index.values[0]
            HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
            HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
            MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
            BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                title="Burden of Diseases diseases statistics comparison among districts.")
            BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
            BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
            BOD_MapData['N']=BOD_MapData['N'].fillna(0)
            BOD_Map= px.choropleth(BOD_MapData,
                    geojson=GPD_MAP.geometry,
                    locations='geo_index',
                    color_continuous_scale="burgyl",
                    color='N',
                    hover_data= ['ADM2_TH','N'],
                    projection="mercator")
            dimension_dict['level'] = grp  
            BOD_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
            )                                                                                                           
            BOD_Map.update_geos(fitbounds="locations", visible=False)
        elif (GrpValue=='ADM1_TH'):
            #print("Triggered from ",button_clicked)
            ResText='Result text from None'
            #print(".................INITIAL MAP...........",BOD_AreaName)
            BOD_AreaName='ตราด'
            page_current=0
            RetText='Waiting for area selection-Area level click Province'
            DiseaseDf=BOD_df[BOD_df['ADM1_TH']==BOD_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf=BOD_df[BOD_df['ADM1_TH']==BOD_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            BOD_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                title="Burden of Diseases diseases statistics of province")
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
            HighLightDisease = []
            HighLightArea = []
            BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
            BOD_MapData['N']=BOD_MapData['N'].fillna(0)
            BOD_Map = px.choropleth(BOD_MapData,
                    geojson=BOD_MapData['geometry'],
                    locations=BOD_MapData.index,
                    color_continuous_scale="burgyl",
                    color="N",
                    hover_data= ['ADM2_TH','N'],
                    projection="mercator")
            dimension_dict['level'] = grp           
            BOD_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
            )                                                                                                          
            BOD_Map.update_geos(fitbounds="locations", visible=False)
            #print("End of INITIAL level")
        elif(GrpValue=='ADM3_TH'):
            Pos=0
            BOD_AreaName=BOD_InitialSubdistrict
            RetText=f'District name: {BOD_AreaName}'
            DiseaseDf=BOD_df[BOD_df['ADM3_TH']==BOD_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            #print(DiseaseDf.head(3))
            Disease_ROW=0
            Pos=0
            #print(DiseaseDf.head(10))
            ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
            AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==BOD_AreaName].index.values[0]
            HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
            HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
            MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
            BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'Sub district', 'N':'Number of cases(N)'},text_auto=True,
                title="Burden of Diseases diseases statistics comparison among districts.")
            BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
            BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
            BOD_MapData['N']=BOD_MapData['N'].fillna(0)
            BOD_Map= px.choropleth(BOD_MapData,
                    geojson=GPD_MAP.geometry,
                    locations='geo_index',
                    color_continuous_scale="burgyl",
                    color='N',
                    hover_data= ['ADM2_TH','ADM3_TH','N'],
                    projection="mercator")
            BOD_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
            )
            dimension_dict['level'] = grp                                                                                                             
            BOD_Map.update_geos(fitbounds="locations", visible=False)
        else:    
            TambonText='ตราด'
            GrpValue='ADM1_TH'
            RetText='Waiting for area selection - Else Area'
            DiseaseDf=BOD_df[BOD_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf=BOD_df[BOD_df['ADM1_TH']==TambonText].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf_Table=AreaDf.to_dict('records')
            BOD_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', text_auto=True,
                title="Burden of Diseases diseases statistics of ..zz.. "+ TambonText)
    elif(button_clicked=='BOD_DiseasesTable'): 
        if active_cell:
            Pos=(page_current*page_size)+active_cell['row']
            #print("Active cell")
            #print("Page current={},size={},row={},Pos={}".format(page_current,page_size,active_cell['row'],Pos))
            if (GrpValue=='ADM1_TH'):
                #print("COMing here")
                RetText=''
                ResText="ONLY Total visits from TRAT PROVINCE ONLY to compare among districts/sub districts choose District/sub district first!"
            elif (GrpValue=='ADM2_TH'):
                RetText=f'District name: {BOD_AreaName}'
                Pos=(page_current*page_size)+active_cell['row']
                #print(DiseaseDf.head(20))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==BOD_AreaName].index.values[0]
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                Disease_ROW=active_cell['row']
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics comparison among districts.")
                BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
                BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                BOD_MapData['N']=BOD_MapData['N'].fillna(0)
                BOD_Map= px.choropleth(BOD_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','N'],
                        projection="mercator")
                dimension_dict['level'] = grp   
                
                BOD_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
                )                                                                                                                 
                BOD_Map.update_geos(fitbounds="locations", visible=False)
            elif (GrpValue=='ADM3_TH'):
                RetText=f'District name: {BOD_AreaName}'
                Pos=(page_current*page_size)+active_cell['row']
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==BOD_AreaName].index.values[0]
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                Disease_ROW=active_cell['row']
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics comparison among districts.")
                BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
                BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
                BOD_MapData['N']=BOD_MapData['N'].fillna(0)
                BOD_Map= px.choropleth(BOD_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','ADM3_TH','N'],
                        projection="mercator")
                dimension_dict['level'] = grp     
                BOD_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
                )
                BOD_Map.update_geos(fitbounds="locations", visible=False)
            else:
                print("Wrong GrpValue=",GrpValue)
        else:
            if(GrpValue=='ADM1_TH'):
                #print("no clicked and diseases table updated with level 1")
                TambonText='ตราด'
                GrpValue='ADM1_TH'
                RetText='Waiting for area selection - ADM1TH'
                DiseaseDf=BOD_df[BOD_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf=BOD_df[BOD_df['ADM1_TH']==TambonText].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                BOD_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics of province")
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
            elif(GrpValue=='ADM2_TH'):
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+1
                AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==BOD_AreaName].index.values[0]
                HighLightDisease = [{"if": {"row_index":0}, "background_color":"#ffdbd8"}]
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics comparison among districts.")
                BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
                ResText="Click the table"
                RetText=f'Province name: {BOD_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
            elif(GrpValue=='ADM3_TH'):
                #print("Next page update")
                Pos=(page_current*page_size)+0
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+0
                AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==BOD_AreaName].index.values[0]
                HighLightDisease = [{"if": {"row_index":0}, "background_color":"#ffdbd8"}]
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                BOD_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics comparison among districts.")
                BOD_Bargraph["data"][0]["marker"]["color"] = ["red" if c == BOD_AreaName else "blue" for c in BOD_Bargraph["data"][0]["x"]]
                ResText=DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                RetText=f'Province name: {BOD_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
            else:
                #print("no clicked and diseases table updated with other level or Updated page")
                TambonText=BOD_AreaName
                #print("AREA NAME=",BOD_AreaName); print("Page current=",page_current)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+1
                AreaDf=BOD_df[BOD_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf_Table=AreaDf.to_dict('records')
                BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                BOD_MapData['N']=BOD_MapData['N'].fillna(0)
                BOD_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Burden of Diseases diseases statistics comparison among districts.")
                ResText="Click the table"
                RetText=f'Province name: {BOD_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
        MaxPages=round(DiseaseDf.shape[0]/page_size)+ (DiseaseDf.shape[0] % page_size > 0)
    else:
        #print("Triggered from ",button_clicked)
        ResText='Result text from None'
        #print(".................INITIAL MAP...........",BOD_AreaName)
        BOD_AreaName='ตราด'
        page_current=0
        RetText='Waiting for area selection-Area level click Province'
        DiseaseDf=BOD_df[BOD_df['ADM1_TH']==BOD_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
        AreaDf=BOD_df[BOD_df['ADM1_TH']==BOD_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
        AreaDf_Table=AreaDf.to_dict('records')
        BOD_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
            title="Burden of Diseases diseases statistics of province")
        DiseaseDf_Table=DiseaseDf.iloc[
                page_current*page_size:(page_current+ 1)*page_size
        ].to_dict('records')
        ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
        HighLightDisease = []
        HighLightArea = []
        BOD_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
        BOD_MapData['N']=BOD_MapData['N'].fillna(0)
        BOD_Map = px.choropleth(BOD_MapData,
                   geojson=BOD_MapData['geometry'],
                   color_continuous_scale="burgyl",
                   locations=BOD_MapData.index,
                   color="N",
                   hover_data= ['ADM2_TH','N'],
                   projection="mercator")
        BOD_Map.update_traces(
            hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
        )
        dimension_dict['level'] = grp                                                                                                             
        BOD_Map.update_geos(fitbounds="locations", visible=False)
        #print("End of INITIAL level")
    return RetText,DiseaseDf_Table,AreaDf_Table,BOD_Bargraph,ResText,AreaText,BOD_AreaName,HighLightArea,HighLightDisease, MaxPages, Selected_Cell_Cmd, Selected_Cell_Value, page_current, BOD_Map
