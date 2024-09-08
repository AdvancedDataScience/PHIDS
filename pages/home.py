import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from sidebar2 import *

dash.register_page(
    __name__,
    path='/',
    title='PHDIS',
    name='PHDIS'
)


MyContent="""
The Ministry of Public Health is an informatic-savvy organization that actively seeks valuable information for the sake of health prevention, care, and rehabilitation. Our objective is to enhance Health Adjusted-Life Expectancy (HALE), reduce the burden of diseases, and foster health equity among both Thai and non-Thai populations. In order to tackle health issues affecting both Thai and non-Thai individuals, it is crucial to have a comprehensive understanding of the prevalence of various illnesses and associated hazards.

I propose the development of a health informatics system called the "Provincial Health Integrated Data System (PHIDS)" specifically designed for the Trat provincial health office. Additionally, this system will be made accessible to other provinces and the Ministry of Health in Cambodia, free of charge.

Creating the PHIDS, I will design a data flow plan that starts with the health station and is based on an Internet of Things (IoT) system. This plan will include health posts and public hospitals, which together serve over 90% of all patients in Trat. Next, I will integrate the communicable disease surveillance report system with the Thailand-Cambodia border control data and securely store it in the cloud system as anonymous data.

In order to make use of this large amount of data, I will develop a dashboard that allows for interactive data visualization, analysis, and decision assistance. This system will be based on the integrated data from each year. This analysis will include additional specialized functions to demonstrate the disparity in the quantity of health services and types of diseases between Thai and non-Thai individuals, with the aim of resolving potential health inequality concerns. The initial phase of PHIDS will commence with an interdisciplinary gathering to incorporate the necessary criteria and disclose the data sources for PHIDS in compliance with data privacy legislation.

Through this APE project, I aim to acquire proficiency in several areas like -data and analysis, policy and programs, leadership, management, and governance, and global health leadership.

>
> Created by Dr.Thanawat Wongphan
>

###### Log Note:
###### V.1.5 Created on Sep $8^{th}$ , 2024
###### ---Actual data deploy
###### -----International transfer cases data
###### -----Dead statatistic
###### -----Update footer of all pages
###### -----Update headline of all pages
###### V.1.4 Created on Sep $5^{th}$ , 2024
###### ---Actual data deploy
###### -----Out-patients
###### -----In-patients
###### -----Communicable diseases patients

###### V.1.3 Created on Aug $30^{th}$ , 2024
###### ---Run production server on cloudspaces 

###### V.1.2 Created on Aug $28^{th}$ , 2024
###### ---Heat Map update 
###### ---Diseases Table click update 
###### ---Tooltip update 
###### ---Bar graph update 
###### ---Out patients update 
###### ---In patients update 
###### ---global health patients update 
###### ---death stat update 
###### ---communicable diseases update

###### V.1.1 Created on Aug $3^{rd}$ , 2024 
###### ---Dummy table working out with dash

###### V.1.0 Created on Jul $17^{th}$ , 2024
###### ---Based line template creation
"""


content = html.Div(id='page-content',children=[
            html.H1('PHDIS',className='p-10 bg-info rounded-3 text-center'),
        html.Hr(),
        html.H2('The Provincial Health Integrated Data System (PHIDS)',className='p-3 bg-light rounded-3'),
        html.Br(),
        dcc.Markdown(MyContent, mathjax=True),
        #dcc.Markdown(MyContent,className='p-3 bg-light rounded-3')
        
        ],style=CONTENT_STYLE)
layout = html.Div([sidebar,content])
