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
    path='/deathstat',
    title='Death Stat Analytics Dashboard',
    name='Death Stat Analytics Dashboard'
)
from DB_Man import *
GPD_MAP = gpd.GeoDataFrame.from_file("Map/Trat/Tambol/Trat.shx", encoding = 'utf-8')
GPD_MAP['geo_index'] = GPD_MAP.index
dimension_dict = {'level': 'ADM1_TH'}

PAGE_SIZE=20


content = html.Div(id='page-content',children=[
            dcc.Store(id = "DS_AreaLevel"),
            dcc.Store(id = "DS_AreaName"),
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1('Death statitstic',className=' text-white text-center'),
                    ],className='p-3 bg-info rounded-3 border-1 ')
                ]),
				dbc.Row([
					dbc.Col([
                            html.P("Select data level:"),
                            dcc.RadioItems(
                                id='DS_SelLevel', 
                                options=["Province","District", "Subdistrict"],
                                value="Province",
                                inline=True
                            ),
                            dcc.Graph(id="DS_graph"),
                            html.Br(),
                            dcc.Graph(id="DS_BarChart"),
							],className='p-2 bg-light rounded-3',width=5
					        ),
    
					dbc.Col([
                        
						dbc.Row([
                            html.H2("Diseases table:"),
							html.Div("",id='DS_LevelDetail')
						    ]),
                        dbc.Row([
							    dash_table.DataTable(id='DS_DiseasesTable',
                                columns=[{'name': 'CODE', 'id': 'CODE',"selectable": True},
                                        {'name': 'Disease', 'id': 'Disease',"selectable": True},
                                        {'name': 'N', 'id': 'N',"selectable": True}],
                                    page_current=0,
                                    page_size=PAGE_SIZE,
                                    page_action='custom'
                                )
						    ]),
                        dbc.Row([
                            dbc.Alert(id='DS_message_under_diseases')
                        ]),
                        dbc.Row([
							html.H2("Area comparison table:"),
                            dash_table.DataTable(id='DS_AreaTable',
                                    sort_action="native",
                                    sort_mode="multi",
                                ),
							html.Div("",id='divDS_AreaTable')
						    ]),
                        dbc.Row([
                            
							html.Div("",id='DS_AreaInformation')
						    ],className='p-3  rounded-3 border-0'),
					    ],className='p-2 bg-light rounded-3  border-0',width = 7),
			        ],className='p-3  rounded-3 border-0'),
                    
                html.Hr(),
                dbc.Row([
					dbc.Col(children=[
                            html.H3("Notes:"),
                            html.P("""Aggregated dead data has been retrived from Ministry of Public Health, Certificate Dead data
                                      During year 2021-2023. Only Thai people has been chosen to show.
                                   """)                    
							],className='p-3 bg-info text-white rounded-3')
                    ])
	        ], fluid = True, style= {"marginTop":"30px","marginLeft":"30px"})
        ],style=CONTENT_STYLE)

layout = html.Div([sidebar,content])


@callback(
    Output("DS_AreaTable", "selected_cells"),
    Output("DS_AreaTable", "active_cell"),
    Input('DS_AreaTable', 'active_cell')
)
def ClearAreaClick(ClickData):
    return [],None
@callback(
    Output("DS_LevelDetail", "children"),
    Output("DS_DiseasesTable","data"),
    Output("DS_AreaTable","data"), 
    Output("DS_BarChart", "figure"),
    Output('DS_message_under_diseases', 'children'),
    Output("DS_AreaInformation","children"),
    Output("DS_AreaName","data"),
    Output("DS_AreaTable", "style_data_conditional"),
    Output("DS_DiseasesTable", "style_data_conditional"),
    Output('DS_DiseasesTable', 'page_count'),
    Output("DS_DiseasesTable", "selected_cells"),
    Output("DS_DiseasesTable", "active_cell"),
    Output('DS_DiseasesTable', "page_current"),
    Output("DS_graph", "figure"),
    Input("DS_graph","clickData"),
    Input('DS_DiseasesTable', "page_current"),
    Input('DS_DiseasesTable', "page_size"),
    Input('DS_DiseasesTable', 'active_cell'),
    Input("DS_AreaLevel", "data"),
    Input("ChooseProvince","value"),
    Input("DS_SelLevel", "value"),
    Input("DS_AreaName","data")
)
def UpdateAllWindows(clickData,page_current,page_size,active_cell,DS_AreaLevel,ProvValue,DS_SelLevel,DS_AreaName):
    global df
    global DiseaseDf
    global DiseaseDf_Table
    global AreaDf
    global AreaDf_Table
    global DS_Bargraph
    GrpValue=dimension_dict['level']
    if(DS_SelLevel=='District'):
        #print("Coming here")
        grp='ADM2_TH'
    elif(DS_SelLevel=='Subdistrict'):
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
    dimension_dict['level']=DS_AreaLevel
    #print("WHAT IS CLICKED",button_clicked,"GROUP LEVEL=",GrpValue,"Sel level=",DS_SelLevel,"PAGE CURRENT UP MOST=",page_current)
    MaxPages=5
    AreaText=''
    DS_Map=dash.no_update
    RetText='Initial data'
    
    if(button_clicked=='DS_graph'):
        Selected_Cell_Cmd=[]
        Selected_Cell_Value=None
        if (clickData is not None):
            #print("Map clicked!")
            IndexLocation=clickData['points'][0]['location']
            TambonText=GPD_MAP[GPD_MAP.index==IndexLocation][GrpValue].item()
            dimension_dict['Name']=TambonText
            DS_AreaName=TambonText
            if (GrpValue=='ADM2_TH'):
                Pos=0
                DiseaseDf=DS_df[DS_df['ADM2_TH']==DS_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Disease_ROW=0
                RetText=f'District name: {DS_AreaName}'
                #Pos=1
                #print(DiseaseDf.head(10))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                #print("+++++++++++Code=",DiseaseDf.iloc[Pos]['CODE'])
                AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                #print("AREA DF=")
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==DS_AreaName].index.values[0]
                #print(AreaDf);print("AREA Name=",DS_AreaName)#print("AREA index=",AreaDf.index) #print("AREA Pos=",ADM2_TH_ROW)
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                #print("Disease row=",Disease_ROW)
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
                DS_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics comparison among districts.")
                DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
            elif(GrpValue=='ADM3_TH'):
                RetText=f'District name: {DS_AreaName}'
                Pos=0
                DiseaseDf=DS_df[DS_df['ADM3_TH']==DS_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Disease_ROW=0
                #print(DiseaseDf.head(10))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)                
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM3_TH']==DS_AreaName].index.values[0]
                ADM3_TH_ROW=0
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
                DS_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics comparison among districts.")
                DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
                DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
                DS_MapData['N']=DS_MapData['N'].fillna(0)
                DS_Map= px.choropleth(DS_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','ADM3_TH','N'],
                        projection="mercator")
                DS_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
                )
                dimension_dict['level'] = grp                                                                                                             
                DS_Map.update_geos(fitbounds="locations", visible=False)
            else:
                #print("Whole map clicked")
                RetText=f'Province name: {TambonText}'
                RetText='Waiting for area selection - Whole map clicked'
                #DiseaseDf=DS_df[DS_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                ResText='Result text from whole map'
                #print(".................INITIAL MAP...........",DS_AreaName)
                DS_AreaName='ตราด'
                page_current=0
                RetText='Waiting for area selection-Area level click Province'
                DiseaseDf=DS_df[DS_df['ADM1_TH']==DS_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf=DS_df[DS_df['ADM1_TH']==DS_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                DS_MapData['N']=DS_MapData['N'].fillna(0)
                DS_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics of province")
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
                HighLightDisease = []
                HighLightArea = []
                DS_Map= px.choropleth(DS_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        projection="mercator")
                dimension_dict['level'] = grp  
                                                                                                                           
                DS_Map.update_geos(fitbounds="locations", visible=False)
                #print("End of Re-INITIAL")
    elif(button_clicked=='DS_AreaLevel') | (button_clicked=='DS_SelLevel'):   
        #print("AREA LEVEL CLICKED",GrpValue)
        Selected_Cell_Cmd=[]
        Selected_Cell_Value=None
        page_current=0
        if (GrpValue=='ADM2_TH'):
            Pos=0
            DS_AreaName=DS_InitialDistrict
            DiseaseDf=DS_df[DS_df['ADM2_TH']==DS_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            Disease_ROW=0
            RetText=f'District name: {DS_AreaName}'
            print(DiseaseDf.head(10))
            ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
            #print("+++++++++++Code=",DiseaseDf.iloc[Pos]['CODE'])
            AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==DS_AreaName].index.values[0]
            HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
            HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
            MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
            DS_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                title="Death statitstic diseases statistics comparison among districts.")
            DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
            DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
            DS_MapData['N']=DS_MapData['N'].fillna(0)
            DS_Map= px.choropleth(DS_MapData,
                    geojson=GPD_MAP.geometry,
                    locations='geo_index',
                    color_continuous_scale="burgyl",
                    color='N',
                    hover_data= ['ADM2_TH','N'],
                    projection="mercator")
            dimension_dict['level'] = grp  
            DS_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
            )                                                                                                           
            DS_Map.update_geos(fitbounds="locations", visible=False)
        elif (GrpValue=='ADM1_TH'):
            #print("Triggered from ",button_clicked)
            ResText='Result text from None'
            #print(".................INITIAL MAP...........",DS_AreaName)
            DS_AreaName='ตราด'
            page_current=0
            RetText='Waiting for area selection-Area level click Province'
            DiseaseDf=DS_df[DS_df['ADM1_TH']==DS_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf=DS_df[DS_df['ADM1_TH']==DS_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            DS_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                title="Death statitstic diseases statistics of province")
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
            HighLightDisease = []
            HighLightArea = []
            DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
            DS_MapData['N']=DS_MapData['N'].fillna(0)
            DS_Map = px.choropleth(DS_MapData,
                    geojson=DS_MapData['geometry'],
                    locations=DS_MapData.index,
                    color_continuous_scale="burgyl",
                    color="N",
                    hover_data= ['ADM2_TH','N'],
                    projection="mercator")
            dimension_dict['level'] = grp           
            DS_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
            )                                                                                                          
            DS_Map.update_geos(fitbounds="locations", visible=False)
            #print("End of INITIAL level")
        elif(GrpValue=='ADM3_TH'):
            Pos=0
            DS_AreaName=DS_InitialSubdistrict
            RetText=f'District name: {DS_AreaName}'
            DiseaseDf=DS_df[DS_df['ADM3_TH']==DS_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            #print(DiseaseDf.head(3))
            Disease_ROW=0
            Pos=0
            #print(DiseaseDf.head(10))
            ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
            AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==DS_AreaName].index.values[0]
            HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
            HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
            MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
            DS_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'Sub district', 'N':'Number of cases(N)'},text_auto=True,
                title="Death statitstic diseases statistics comparison among districts.")
            DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
            DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
            DS_MapData['N']=DS_MapData['N'].fillna(0)
            DS_Map= px.choropleth(DS_MapData,
                    geojson=GPD_MAP.geometry,
                    locations='geo_index',
                    color_continuous_scale="burgyl",
                    color='N',
                    hover_data= ['ADM2_TH','ADM3_TH','N'],
                    projection="mercator")
            DS_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
            )
            dimension_dict['level'] = grp                                                                                                             
            DS_Map.update_geos(fitbounds="locations", visible=False)
        else:    
            TambonText='ตราด'
            GrpValue='ADM1_TH'
            RetText='Waiting for area selection - Else Area'
            DiseaseDf=DS_df[DS_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf=DS_df[DS_df['ADM1_TH']==TambonText].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf_Table=AreaDf.to_dict('records')
            DS_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', text_auto=True,
                title="Death statitstic diseases statistics of ..zz.. "+ TambonText)
    elif(button_clicked=='DS_DiseasesTable'): 
        if active_cell:
            Pos=(page_current*page_size)+active_cell['row']
            #print("Active cell")
            #print("Page current={},size={},row={},Pos={}".format(page_current,page_size,active_cell['row'],Pos))
            if (GrpValue=='ADM1_TH'):
                #print("COMing here")
                RetText=''
                ResText="ONLY Total visits from TRAT PROVINCE ONLY to compare among districts/sub districts choose District/sub district first!"
            elif (GrpValue=='ADM2_TH'):
                RetText=f'District name: {DS_AreaName}'
                Pos=(page_current*page_size)+active_cell['row']
                #print(DiseaseDf.head(20))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==DS_AreaName].index.values[0]
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                Disease_ROW=active_cell['row']
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                DS_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics comparison among districts.")
                DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
                DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                DS_MapData['N']=DS_MapData['N'].fillna(0)
                DS_Map= px.choropleth(DS_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','N'],
                        projection="mercator")
                dimension_dict['level'] = grp   
                
                DS_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
                )                                                                                                                 
                DS_Map.update_geos(fitbounds="locations", visible=False)
            elif (GrpValue=='ADM3_TH'):
                RetText=f'District name: {DS_AreaName}'
                Pos=(page_current*page_size)+active_cell['row']
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==DS_AreaName].index.values[0]
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                Disease_ROW=active_cell['row']
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                DS_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics comparison among districts.")
                DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
                DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
                DS_MapData['N']=DS_MapData['N'].fillna(0)
                DS_Map= px.choropleth(DS_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','ADM3_TH','N'],
                        projection="mercator")
                dimension_dict['level'] = grp     
                DS_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
                )
                DS_Map.update_geos(fitbounds="locations", visible=False)
            else:
                print("Wrong GrpValue=",GrpValue)
        else:
            if(GrpValue=='ADM1_TH'):
                #print("no clicked and diseases table updated with level 1")
                TambonText='ตราด'
                GrpValue='ADM1_TH'
                RetText='Waiting for area selection - ADM1TH'
                DiseaseDf=DS_df[DS_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf=DS_df[DS_df['ADM1_TH']==TambonText].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                DS_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics of province")
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
            elif(GrpValue=='ADM2_TH'):
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+1
                AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==DS_AreaName].index.values[0]
                HighLightDisease = [{"if": {"row_index":0}, "background_color":"#ffdbd8"}]
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                DS_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics comparison among districts.")
                DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
                ResText="Click the table"
                RetText=f'Province name: {DS_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
            elif(GrpValue=='ADM3_TH'):
                #print("Next page update")
                Pos=(page_current*page_size)+0
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+0
                AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==DS_AreaName].index.values[0]
                HighLightDisease = [{"if": {"row_index":0}, "background_color":"#ffdbd8"}]
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                DS_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics comparison among districts.")
                DS_Bargraph["data"][0]["marker"]["color"] = ["red" if c == DS_AreaName else "blue" for c in DS_Bargraph["data"][0]["x"]]
                ResText=DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                RetText=f'Province name: {DS_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
            else:
                #print("no clicked and diseases table updated with other level or Updated page")
                TambonText=DS_AreaName
                #print("AREA NAME=",DS_AreaName); print("Page current=",page_current)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+1
                AreaDf=DS_df[DS_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf_Table=AreaDf.to_dict('records')
                DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                DS_MapData['N']=DS_MapData['N'].fillna(0)
                DS_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="Death statitstic diseases statistics comparison among districts.")
                ResText="Click the table"
                RetText=f'Province name: {DS_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
        MaxPages=round(DiseaseDf.shape[0]/page_size)+ (DiseaseDf.shape[0] % page_size > 0)
    else:
        #print("Triggered from ",button_clicked)
        ResText='Result text from None'
        #print(".................INITIAL MAP...........",DS_AreaName)
        DS_AreaName='ตราด'
        page_current=0
        RetText='Waiting for area selection-Area level click Province'
        DiseaseDf=DS_df[DS_df['ADM1_TH']==DS_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
        AreaDf=DS_df[DS_df['ADM1_TH']==DS_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
        AreaDf_Table=AreaDf.to_dict('records')
        DS_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
            title="Death statitstic diseases statistics of province")
        DiseaseDf_Table=DiseaseDf.iloc[
                page_current*page_size:(page_current+ 1)*page_size
        ].to_dict('records')
        ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
        HighLightDisease = []
        HighLightArea = []
        DS_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
        DS_MapData['N']=DS_MapData['N'].fillna(0)
        DS_Map = px.choropleth(DS_MapData,
                   geojson=DS_MapData['geometry'],
                   color_continuous_scale="burgyl",
                   locations=DS_MapData.index,
                   color="N",
                   hover_data= ['ADM2_TH','N'],
                   projection="mercator")
        DS_Map.update_traces(
            hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
        )
        dimension_dict['level'] = grp                                                                                                             
        DS_Map.update_geos(fitbounds="locations", visible=False)
        #print("End of INITIAL level")
    return RetText,DiseaseDf_Table,AreaDf_Table,DS_Bargraph,ResText,AreaText,DS_AreaName,HighLightArea,HighLightDisease, MaxPages, Selected_Cell_Cmd, Selected_Cell_Value, page_current, DS_Map
