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
    path='/globalhealth',
    title='Global Health Dashboard',
    name='Global Health Dashboard'
)
from DB_Man import *
GPD_MAP = gpd.GeoDataFrame.from_file("Map/Trat/Tambol/Trat.shx", encoding = 'utf-8')
GPD_MAP['geo_index'] = GPD_MAP.index
dimension_dict = {'level': 'ADM1_TH'}

PAGE_SIZE=20


content = html.Div(id='page-content',children=[
            dcc.Store(id = "GH_AreaLevel"),
            dcc.Store(id = "GH_AreaName"),
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1('Global health and international health',className=' text-white text-center'),
                    ],className='p-3 bg-info rounded-3 border-1 ')
                ]),
				dbc.Row([
					dbc.Col([
                            html.P("Select data level:"),
                            dcc.RadioItems(
                                id='GH_SelLevel', 
                                options=["Province","District", "Subdistrict"],
                                value="Province",
                                inline=True
                            ),
                            dcc.Graph(id="GH_graph"),
                            html.Br(),
                            dcc.Graph(id="GH_BarChart"),
							],className='p-2 bg-light rounded-3',width=5
					        ),
    
					dbc.Col([
                        
						dbc.Row([
                            html.H2("Diseases table:"),
							html.Div("",id='GH_LevelDetail')
						    ]),
                        dbc.Row([
							    dash_table.DataTable(id='GH_DiseasesTable',
                                columns=[{'name': 'CODE', 'id': 'CODE',"selectable": True},
                                        {'name': 'Disease', 'id': 'Disease',"selectable": True},
                                        {'name': 'N', 'id': 'N',"selectable": True}],
                                    page_current=0,
                                    page_size=PAGE_SIZE,
                                    page_action='custom'
                                )
						    ]),
                        dbc.Row([
                            dbc.Alert(id='GH_message_under_diseases')
                        ]),
                        dbc.Row([
							html.H2("Area comparison table:"),
                            dash_table.DataTable(id='GH_AreaTable',
                                    sort_action="native",
                                    sort_mode="multi",
                                ),
							html.Div("",id='divGH_AreaTable')
						    ]),
                        dbc.Row([
                            
							html.Div("",id='GH_AreaInformation')
						    ],className='p-3  rounded-3 border-0'),
					    ],className='p-2 bg-light rounded-3  border-0',width = 7),
			        ],className='p-3  rounded-3 border-0'),
                    
                html.Hr(),
                dbc.Row([
					dbc.Col(children=[
                            html.H3("Note:", style={'color': 'yellow'}),
                            html.Div("""Compiled from the consolidated referral data obtained from Koh Kong, Khlong Yai, Trat Hospital, and Bangkok-Trat Hospital. 
For instances beyond 100, there is no distinct pattern of occurrence. 
Nevertheless, the data revealed that half of the top ten disorders were infectious, 
while the remaining about half of referral data were attributed to traumatic accidents and 
stroke which some of them requiring surgical procedures and advanced diagnostic procedures.
""", style={'color': 'white', 'fontSize': 20}),
                            dcc.Markdown("***"),
                            html.Div("Policy recommendations:", style={'color': 'yellow', 'fontSize': 30}),
                            html.Div("1. Infectious diseases:", style={'color': 'yellow', 'fontSize': 25}),
                            dcc.Markdown("""
The policy recommendations to enhance readiness for trans-border referral infectious cases are as follows:

* 1.1 Maintain a broader range of medications at Klong Yai Hospital, including those that specifically target lung infections and urinary tract inflammations.

* 1.2 Setting up the infection control network, prepared for consultation among Khlong yai, Koh Kong, and infectious specialists. It is recommended to broaden this choice to include TB infection, particularly at the lung location.

* 1.3 It is advisable to avoid using the most potent broad spectrum antibiotics, including drug-resistant antibiotics, because of the straightforward nature of the infections. However, if the culture results suggest otherwise, Khlong Yai should be prepared to promptly and effectively coordinate logistics from Trat hospital.

* 1.4 Koh Khong Hospital should be prepared to promptly gather specimens for culture relevant to illnesses, particularly sputum culture. Khlong Yai Hospital may solicit contributions or engage in partnership with an NGO to offer this service without any cost. Management of contaminated culture medium should adhere to worldwide standard protocols.""", style={'color': 'white', 'fontSize': 20}),
        html.Div("2. Non-infectious diseases:", style={'color': 'yellow', 'fontSize': 25}),                                 
dcc.Markdown("""
* 2.1 Considering the significant number of stroke cases from Koh Khong, it is advised to arrange a CT scan to promptly and precisely identify the causes of the stroke.
* 2.2 One patient was moved to Chantaburi due to insufficient health services available on that day. Hence, Khlong yai should develop a prompt transfer case plan, which includes the utilization of a helicopter, after an accurate diagnosis.
* 2.3 If a stroke has been identified but no surgery is required, Khlong Yai should be prepared to provide conservative care for stroke cases, which may include reducing brain swelling with hyperosmolar drugs like mannitol, etc., until the recovery phase that requires rehabilitation.
* 2.4 It is recommended that Koh Khong build a rehabilitation network to provide care for individuals upon their release from Wither Khlong Yai or Trat Province.

Conclusively, all eight health policy recommendations require assistance from both the government and non-government sectors in the provinces. Instead of focusing on the care process, these policies should be evaluated based on the overall development in one year and the end outcome of patients.

""", style={'color': 'white', 'fontSize': 20}),
                            html.P(),
                            html.Div("""* NOTE: International reffered patients' data has been subtracted from the refereal
                                   data system(Trat, Thailand - Koh Khong, Cambodia) since 2017-2022. 
                                   During COVID-19 outbreak, there was no case could be transferred due to closed border policy.
                                   """, style={'color': 'white', 'fontSize': 14}),
                                              
							])
                    ],className='p-3 bg-info text-white rounded-3'),
            dbc.Row([
					dbc.Col(children=[
                            html.H3("Cambodian Note:", style={'color': 'yellow'}),
                            html.Div("""Compiled from the consolidated referral data obtained from Koh Kong, Khlong Yai, Trat Hospital, and Bangkok-Trat Hospital. 
For instances beyond 100, there is no distinct pattern of occurrence. 
Nevertheless, the data revealed that half of the top ten disorders were infectious, 
while the remaining about half of referral data were attributed to traumatic accidents and 
stroke which some of them requiring surgical procedures and advanced diagnostic procedures.
""", style={'color': 'white', 'fontSize': 20}),
                            dcc.Markdown("***"),
                            html.Div("Policy recommendations:", style={'color': 'yellow', 'fontSize': 30}),
                            html.Div("1. Infectious diseases:", style={'color': 'yellow', 'fontSize': 25}),
                            dcc.Markdown("""
The policy recommendations to enhance readiness for trans-border referral infectious cases are as follows:

* 1.1 Maintain a broader range of medications at Klong Yai Hospital, including those that specifically target lung infections and urinary tract inflammations.

* 1.2 Setting up the infection control network, prepared for consultation among Khlong yai, Koh Kong, and infectious specialists. It is recommended to broaden this choice to include TB infection, particularly at the lung location.

* 1.3 It is advisable to avoid using the most potent broad spectrum antibiotics, including drug-resistant antibiotics, because of the straightforward nature of the infections. However, if the culture results suggest otherwise, Khlong Yai should be prepared to promptly and effectively coordinate logistics from Trat hospital.

* 1.4 Koh Khong Hospital should be prepared to promptly gather specimens for culture relevant to illnesses, particularly sputum culture. Khlong Yai Hospital may solicit contributions or engage in partnership with an NGO to offer this service without any cost. Management of contaminated culture medium should adhere to worldwide standard protocols.""", style={'color': 'white', 'fontSize': 20}),
        html.Div("2. Non-infectious diseases:", style={'color': 'yellow', 'fontSize': 25}),                                 
dcc.Markdown("""
* 2.1 Considering the significant number of stroke cases from Koh Khong, it is advised to arrange a CT scan to promptly and precisely identify the causes of the stroke.
* 2.2 One patient was moved to Chantaburi due to insufficient health services available on that day. Hence, Khlong yai should develop a prompt transfer case plan, which includes the utilization of a helicopter, after an accurate diagnosis.
* 2.3 If a stroke has been identified but no surgery is required, Khlong Yai should be prepared to provide conservative care for stroke cases, which may include reducing brain swelling with hyperosmolar drugs like mannitol, etc., until the recovery phase that requires rehabilitation.
* 2.4 It is recommended that Koh Khong build a rehabilitation network to provide care for individuals upon their release from Wither Khlong Yai or Trat Province.

Conclusively, all eight health policy recommendations require assistance from both the government and non-government sectors in the provinces. Instead of focusing on the care process, these policies should be evaluated based on the overall development in one year and the end outcome of patients.

""", style={'color': 'white', 'fontSize': 20}),
                            html.P(),
                            html.Div("""* NOTE: International reffered patients' data has been subtracted from the refereal
                                   data system(Trat, Thailand - Koh Khong, Cambodia) since 2017-2022. 
                                   During COVID-19 outbreak, there was no case could be transferred due to closed border policy.
                                   """, style={'color': 'white', 'fontSize': 14}),
                                              
							])
                    ],className='p-3 bg-success text-white rounded-3')
	        ], fluid = True, style= {"marginTop":"30px","marginLeft":"30px"})
        ],style=CONTENT_STYLE)

layout = html.Div([sidebar,content])


@callback(
    Output("GH_AreaTable", "selected_cells"),
    Output("GH_AreaTable", "active_cell"),
    Input('GH_AreaTable', 'active_cell')
)
def ClearAreaClick(ClickData):
    return [],None
@callback(
    Output("GH_LevelDetail", "children"),
    Output("GH_DiseasesTable","data"),
    Output("GH_AreaTable","data"), 
    Output("GH_BarChart", "figure"),
    Output('GH_message_under_diseases', 'children'),
    Output("GH_AreaInformation","children"),
    Output("GH_AreaName","data"),
    Output("GH_AreaTable", "style_data_conditional"),
    Output("GH_DiseasesTable", "style_data_conditional"),
    Output('GH_DiseasesTable', 'page_count'),
    Output("GH_DiseasesTable", "selected_cells"),
    Output("GH_DiseasesTable", "active_cell"),
    Output('GH_DiseasesTable', "page_current"),
    Output("GH_graph", "figure"),
    Input("GH_graph","clickData"),
    Input('GH_DiseasesTable', "page_current"),
    Input('GH_DiseasesTable', "page_size"),
    Input('GH_DiseasesTable', 'active_cell'),
    Input("GH_AreaLevel", "data"),
    Input("ChooseProvince","value"),
    Input("GH_SelLevel", "value"),
    Input("GH_AreaName","data")
)
def UpdateAllWindows(clickData,page_current,page_size,active_cell,GH_AreaLevel,ProvValue,GH_SelLevel,GH_AreaName):
    global df
    global DiseaseDf
    global DiseaseDf_Table
    global AreaDf
    global AreaDf_Table
    global GH_Bargraph
    GrpValue=dimension_dict['level']
    if(GH_SelLevel=='District'):
        #print("Coming here")
        grp='ADM2_TH'
    elif(GH_SelLevel=='Subdistrict'):
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
    dimension_dict['level']=GH_AreaLevel
    #print("WHAT IS CLICKED",button_clicked,"GROUP LEVEL=",GrpValue,"Sel level=",GH_SelLevel,"PAGE CURRENT UP MOST=",page_current)
    MaxPages=5
    AreaText=''
    GH_Map=dash.no_update
    RetText='Initial data'
    
    if(button_clicked=='GH_graph'):
        Selected_Cell_Cmd=[]
        Selected_Cell_Value=None
        if (clickData is not None):
            #print("Map clicked!")
            IndexLocation=clickData['points'][0]['location']
            TambonText=GPD_MAP[GPD_MAP.index==IndexLocation][GrpValue].item()
            dimension_dict['Name']=TambonText
            GH_AreaName=TambonText
            if (GrpValue=='ADM2_TH'):
                Pos=0
                DiseaseDf=GH_df[GH_df['ADM2_TH']==GH_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Disease_ROW=0
                RetText=f'District name: {GH_AreaName}'
                #Pos=1
                #print(DiseaseDf.head(10))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                #print("+++++++++++Code=",DiseaseDf.iloc[Pos]['CODE'])
                AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                #print("AREA DF=")
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==GH_AreaName].index.values[0]
                #print(AreaDf);print("AREA Name=",GH_AreaName)#print("AREA index=",AreaDf.index) #print("AREA Pos=",ADM2_TH_ROW)
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                #print("Disease row=",Disease_ROW)
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
                GH_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="International health diseases statistics comparison among districts.")
                GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
            elif(GrpValue=='ADM3_TH'):
                RetText=f'District name: {GH_AreaName}'
                Pos=0
                DiseaseDf=GH_df[GH_df['ADM3_TH']==GH_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Disease_ROW=0
                #print(DiseaseDf.head(10))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)                
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM3_TH']==GH_AreaName].index.values[0]
                ADM3_TH_ROW=0
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
                GH_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="International health diseases statistics comparison among districts.")
                GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
                GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
                GH_MapData['N']=GH_MapData['N'].fillna(0)
                GH_Map= px.choropleth(GH_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','ADM3_TH','N'],
                        projection="mercator")
                GH_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
                )
                dimension_dict['level'] = grp                                                                                                             
                GH_Map.update_geos(fitbounds="locations", visible=False)
            else:
                #print("Whole map clicked")
                RetText=f'Province name: {TambonText}'
                RetText='Waiting for area selection - Whole map clicked'
                #DiseaseDf=GH_df[GH_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                ResText='Result text from whole map'
                #print(".................INITIAL MAP...........",GH_AreaName)
                GH_AreaName='ตราด'
                page_current=0
                RetText='Waiting for area selection-Area level click Province'
                DiseaseDf=GH_df[GH_df['ADM1_TH']==GH_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf=GH_df[GH_df['ADM1_TH']==GH_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                GH_MapData['N']=GH_MapData['N'].fillna(0)
                GH_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                    title="International health diseases statistics of province")
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
                HighLightDisease = []
                HighLightArea = []
                GH_Map= px.choropleth(GH_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        projection="mercator")
                dimension_dict['level'] = grp  
                                                                                                                           
                GH_Map.update_geos(fitbounds="locations", visible=False)
                #print("End of Re-INITIAL")
    elif(button_clicked=='GH_AreaLevel') | (button_clicked=='GH_SelLevel'):   
        #print("AREA LEVEL CLICKED",GrpValue)
        Selected_Cell_Cmd=[]
        Selected_Cell_Value=None
        page_current=0
        if (GrpValue=='ADM2_TH'):
            Pos=0
            GH_AreaName=GH_InitialDistrict
            DiseaseDf=GH_df[GH_df['ADM2_TH']==GH_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            Disease_ROW=0
            RetText=f'District name: {GH_AreaName}'
            print(DiseaseDf.head(10))
            ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
            #print("+++++++++++Code=",DiseaseDf.iloc[Pos]['CODE'])
            AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==GH_AreaName].index.values[0]
            HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
            HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
            MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
            GH_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                title="International health diseases statistics comparison among districts.")
            GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
            GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
            GH_MapData['N']=GH_MapData['N'].fillna(0)
            GH_Map= px.choropleth(GH_MapData,
                    geojson=GPD_MAP.geometry,
                    locations='geo_index',
                    color_continuous_scale="burgyl",
                    color='N',
                    hover_data= ['ADM2_TH','N'],
                    projection="mercator")
            dimension_dict['level'] = grp  
            GH_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
            )                                                                                                           
            GH_Map.update_geos(fitbounds="locations", visible=False)
        elif (GrpValue=='ADM1_TH'):
            #print("Triggered from ",button_clicked)
            ResText='Result text from None'
            #print(".................INITIAL MAP...........",GH_AreaName)
            GH_AreaName='ตราด'
            page_current=0
            RetText='Waiting for area selection-Area level click Province'
            DiseaseDf=GH_df[GH_df['ADM1_TH']==GH_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf=GH_df[GH_df['ADM1_TH']==GH_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            GH_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                title="International health diseases statistics of province")
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
            HighLightDisease = []
            HighLightArea = []
            GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
            GH_MapData['N']=GH_MapData['N'].fillna(0)
            GH_Map = px.choropleth(GH_MapData,
                    geojson=GH_MapData['geometry'],
                    locations=GH_MapData.index,
                    color_continuous_scale="burgyl",
                    color="N",
                    hover_data= ['ADM2_TH','N'],
                    projection="mercator")
            dimension_dict['level'] = grp           
            GH_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
            )                                                                                                          
            GH_Map.update_geos(fitbounds="locations", visible=False)
            #print("End of INITIAL level")
        elif(GrpValue=='ADM3_TH'):
            Pos=0
            GH_AreaName=GH_InitialSubdistrict
            RetText=f'District name: {GH_AreaName}'
            DiseaseDf=GH_df[GH_df['ADM3_TH']==GH_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            DiseaseDf_Table=DiseaseDf.iloc[
                    page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            #print(DiseaseDf.head(3))
            Disease_ROW=0
            Pos=0
            #print(DiseaseDf.head(10))
            ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
            AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
            AreaDf_Table=AreaDf.to_dict('records')
            ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==GH_AreaName].index.values[0]
            HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
            HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
            MaxPages=round(DiseaseDf.size/page_size)+ (DiseaseDf.size % page_size > 0)
            GH_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'Sub district', 'N':'Number of cases(N)'},text_auto=True,
                title="International health diseases statistics comparison among districts.")
            GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
            GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
            GH_MapData['N']=GH_MapData['N'].fillna(0)
            GH_Map= px.choropleth(GH_MapData,
                    geojson=GPD_MAP.geometry,
                    locations='geo_index',
                    color_continuous_scale="burgyl",
                    color='N',
                    hover_data= ['ADM2_TH','ADM3_TH','N'],
                    projection="mercator")
            GH_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
            )
            dimension_dict['level'] = grp                                                                                                             
            GH_Map.update_geos(fitbounds="locations", visible=False)
        else:    
            TambonText='ตราด'
            GrpValue='ADM1_TH'
            RetText='Waiting for area selection - Else Area'
            DiseaseDf=GH_df[GH_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf=GH_df[GH_df['ADM1_TH']==TambonText].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
            AreaDf_Table=AreaDf.to_dict('records')
            GH_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', text_auto=True,
                title="International health diseases statistics of ..zz.. "+ TambonText)
    elif(button_clicked=='GH_DiseasesTable'): 
        if active_cell:
            Pos=(page_current*page_size)+active_cell['row']
            #print("Active cell")
            #print("Page current={},size={},row={},Pos={}".format(page_current,page_size,active_cell['row'],Pos))
            if (GrpValue=='ADM1_TH'):
                #print("COMing here")
                RetText=''
                ResText="ONLY Total visits from TRAT PROVINCE ONLY to compare among districts/sub districts choose District/sub district first!"
            elif (GrpValue=='ADM2_TH'):
                RetText=f'District name: {GH_AreaName}'
                Pos=(page_current*page_size)+active_cell['row']
                #print(DiseaseDf.head(20))
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==GH_AreaName].index.values[0]
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                Disease_ROW=active_cell['row']
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                GH_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="International health diseases statistics comparison among districts.")
                GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
                GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                GH_MapData['N']=GH_MapData['N'].fillna(0)
                GH_Map= px.choropleth(GH_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','N'],
                        projection="mercator")
                dimension_dict['level'] = grp   
                
                GH_Map.update_traces(
                    hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
                )                                                                                                                 
                GH_Map.update_geos(fitbounds="locations", visible=False)
            elif (GrpValue=='ADM3_TH'):
                RetText=f'District name: {GH_AreaName}'
                Pos=(page_current*page_size)+active_cell['row']
                ResText = DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==GH_AreaName].index.values[0]
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                Disease_ROW=active_cell['row']
                HighLightDisease = [{"if": {"row_index":Disease_ROW}, "background_color":"#ffdbd8"}]
                GH_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="International health diseases statistics comparison among districts.")
                GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
                GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM3_TH")
                GH_MapData['N']=GH_MapData['N'].fillna(0)
                GH_Map= px.choropleth(GH_MapData,
                        geojson=GPD_MAP.geometry,
                        locations='geo_index',
                        color_continuous_scale="burgyl",
                        color='N',
                        hover_data= ['ADM2_TH','ADM3_TH','N'],
                        projection="mercator")
                dimension_dict['level'] = grp     
                GH_Map.update_traces(
                        hovertemplate="<b>อ.%{customdata[0]}</b><br>ต.%{customdata[1]}<br>จำนวน: %{customdata[2]}"
                )
                GH_Map.update_geos(fitbounds="locations", visible=False)
            else:
                print("Wrong GrpValue=",GrpValue)
        else:
            if(GrpValue=='ADM1_TH'):
                #print("no clicked and diseases table updated with level 1")
                TambonText='ตราด'
                GrpValue='ADM1_TH'
                RetText='Waiting for area selection - ADM1TH'
                DiseaseDf=GH_df[GH_df['ADM1_TH']==TambonText].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf=GH_df[GH_df['ADM1_TH']==TambonText].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                GH_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
                    title="International health diseases statistics of province")
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
            elif(GrpValue=='ADM2_TH'):
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+1
                AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM2_TH_ROW=AreaDf[AreaDf['ADM2_TH']==GH_AreaName].index.values[0]
                HighLightDisease = [{"if": {"row_index":0}, "background_color":"#ffdbd8"}]
                HighLightArea = [{"if": {"row_index":ADM2_TH_ROW}, "background_color":"#ffdbd8"}]
                GH_Bargraph = px.bar(AreaDf, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="International health diseases statistics comparison among districts.")
                GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
                ResText="Click the table"
                RetText=f'Province name: {GH_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
            elif(GrpValue=='ADM3_TH'):
                #print("Next page update")
                Pos=(page_current*page_size)+0
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+0
                AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM3_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
                AreaDf_Table=AreaDf.to_dict('records')
                ADM3_TH_ROW=AreaDf[AreaDf['ADM3_TH']==GH_AreaName].index.values[0]
                HighLightDisease = [{"if": {"row_index":0}, "background_color":"#ffdbd8"}]
                HighLightArea = [{"if": {"row_index":ADM3_TH_ROW}, "background_color":"#ffdbd8"}]
                GH_Bargraph = px.bar(AreaDf, y='N', x='ADM3_TH', labels={'ADM3_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="International health diseases statistics comparison among districts.")
                GH_Bargraph["data"][0]["marker"]["color"] = ["red" if c == GH_AreaName else "blue" for c in GH_Bargraph["data"][0]["x"]]
                ResText=DiseaseDf.iloc[Pos]['CODE']+ " " + DiseaseDf.iloc[Pos]['Disease']
                RetText=f'Province name: {GH_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
            else:
                #print("no clicked and diseases table updated with other level or Updated page")
                TambonText=GH_AreaName
                #print("AREA NAME=",GH_AreaName); print("Page current=",page_current)
                DiseaseDf_Table=DiseaseDf.iloc[
                        page_current*page_size:(page_current+ 1)*page_size
                ].to_dict('records')
                Pos=(page_current*page_size)+1
                AreaDf=GH_df[GH_df['CODE']==DiseaseDf.iloc[Pos]['CODE']].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
                AreaDf_Table=AreaDf.to_dict('records')
                GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
                GH_MapData['N']=GH_MapData['N'].fillna(0)
                GH_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Number of cases(N)'},text_auto=True,
                    title="International health diseases statistics comparison among districts.")
                ResText="Click the table"
                RetText=f'Province name: {GH_AreaName}'
                AreaText="Choose the disease from upper table for comparisons."
        MaxPages=round(DiseaseDf.shape[0]/page_size)+ (DiseaseDf.shape[0] % page_size > 0)
    else:
        #print("Triggered from ",button_clicked)
        ResText='Result text from None'
        #print(".................INITIAL MAP...........",GH_AreaName)
        GH_AreaName='ตราด'
        page_current=0
        RetText='Waiting for area selection-Area level click Province'
        DiseaseDf=GH_df[GH_df['ADM1_TH']==GH_AreaName].groupby(['CODE','Disease']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False)
        AreaDf=GH_df[GH_df['ADM1_TH']==GH_AreaName].groupby(['ADM2_TH']).agg({'N': 'count'}).reset_index().sort_values(['N'],ascending=False).reset_index(drop=True)
        AreaDf_Table=AreaDf.to_dict('records')
        GH_Bargraph = px.bar(AreaDf_Table, y='N', x='ADM2_TH', labels={'ADM2_TH': 'District', 'N':'Total OPD cases(N)'},text_auto=True,
            title="International health diseases statistics of province")
        DiseaseDf_Table=DiseaseDf.iloc[
                page_current*page_size:(page_current+ 1)*page_size
        ].to_dict('records')
        ResText="To choose district/ sub-district area data, proceed to choose level from the top-left options of the map."
        HighLightDisease = []
        HighLightArea = []
        GH_MapData=GPD_MAP.merge(AreaDf, how='left', on="ADM2_TH")
        GH_MapData['N']=GH_MapData['N'].fillna(0)
        GH_Map = px.choropleth(GH_MapData,
                   geojson=GH_MapData['geometry'],
                   color_continuous_scale="burgyl",
                   locations=GH_MapData.index,
                   color="N",
                   hover_data= ['ADM2_TH','N'],
                   projection="mercator")
        GH_Map.update_traces(
            hovertemplate="<b>อ.%{customdata[0]}</b><br>จำนวน: %{customdata[1]}"
        )
        dimension_dict['level'] = grp                                                                                                             
        GH_Map.update_geos(fitbounds="locations", visible=False)
        #print("End of INITIAL level")
    return RetText,DiseaseDf_Table,AreaDf_Table,GH_Bargraph,ResText,AreaText,GH_AreaName,HighLightArea,HighLightDisease, MaxPages, Selected_Cell_Cmd, Selected_Cell_Value, page_current, GH_Map
