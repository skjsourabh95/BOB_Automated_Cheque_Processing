import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import base64
import datetime
import io,os
from flask import Flask, send_from_directory
from common.header import header_layout
from app import app
import warnings
from pandas.core.common import SettingWithCopyWarning
import json
from scripts.process import process_cheque
from scripts.translate import translate_cheque
from scripts.storage import get_all


from PIL import Image
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)

UPLOADED_FILE_NAME = None

UPLOAD_DIRECTORY = "./data/app_uploaded_files"
PROCESS_DIRECTORY = "./data/tmp"

reduction = None

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


layout =    html.Div([
                header_layout,
                html.Br(),
                html.Div([
                    dcc.Tabs([
                        dcc.Tab(label='Upload Files', children=[
                            html.Div([  
                                html.H2("Upload"),
                                dcc.Upload(
                                    id="upload-data",
                                    children=html.Div([
                                    'Drag and Drop an Image or ',
                                    html.A('Select Image')
                                    ]),
                                    style={
                                        "width": "100%",
                                        "height": "60px",
                                        "lineHeight": "60px",
                                        "borderWidth": "1px",
                                        "borderStyle": "dashed",
                                        "borderRadius": "5px",
                                        "textAlign": "center",
                                        "margin": "10px",
                                    },
                                    multiple=False,
                                ), 
                            ],style={"max-width": "500px","textAlign": "center","justify-content": "center","align-items": "center"}),
                            html.Div([
                                dcc.Loading(
                                        id="loading",
                                        type="dot",
                                        children=html.Div(id="loading-output")
                                ),
                            ]),
                            html.Div([
                                html.Div([
                                    dcc.ConfirmDialogProvider(
                                        children=html.Button(
                                            'Process',className='roundbutton',style={'backgroundColor': 'blue', 'color':'white'}
                                        ),
                                        id='submit-provider',
                                        message='Are you sure you want to continue?'
                                    ),
                                    html.Br(),
                                    html.Div([
                                        dcc.Loading(
                                                id="loading-1",
                                                type="default",
                                                children=html.Div(id="loading-confirm")
                                        ),
                                    ]),
                                html.Div(id='output-provider'),],style={"textAlign": "center","justify-content": "center","align-items": "center"}),
                            ],style={"max-width": "500px"}),
                            html.Div([
                                    html.Div(id='output-image-data')
                                ]),
                        ]),
                        dcc.Tab(label='Image Optimization', children=[
                            html.Div([
                                html.H2("Optimization View"),
                            ],
                            style={
                                "textAlign": "center",
                                "justify-content": "center",
                                "align-items": "center"}
                            ),  
                            html.Div([
                                html.Div(id='optimize-data-upload'),
                            ]),
                        ]),
                        dcc.Tab(label='Attribute Extraction', children=[
                            html.Div([
                                html.H2("Extraction View"),
                            ],
                            style={
                                "textAlign": "center",
                                "justify-content": "center",
                                "align-items": "center"}
                            ),  
                            html.Div(children=[
                                html.Div([
                                    html.Div(id='extract-data-upload'),
                                ],className="six columns"),
                                html.Div([
                                    html.Div([html.Div(id='extract-data-table')]),
                                    html.Br(),
                                    html.Br(),
                                    html.Div([
                                        html.Div([
                                            html.Button('Translate', id='btn-translate', n_clicks=0,className='roundbutton',style={'backgroundColor': 'blue', 'color':'white','margin-right':'16px'}),
                                            html.Br(),
                                            html.Br(),
                                            html.Div([
                                                dcc.Loading(
                                                        id="loading-2",
                                                        type="default",
                                                        children=html.Div(id="loading-translate")
                                                    ),
                                                ]),
                                        ],style={"textAlign": "center",
                                            "width": "50%",
                                            "margin": "auto"}
                                        ),
                                    ]),
                                ],className="six columns")
                            ]),
                        ]),
                        dcc.Tab(label='Signature Verification', children=[
                            html.Div([
                                html.H2("Verification View"),
                            ],
                            style={
                                "textAlign": "center",
                                "justify-content": "center",
                                "align-items": "center"}
                            ),  
                            html.Div(children=[
                                html.Div([
                                    html.Div(id='sign-data-upload'),
                                ],className="six columns"),
                                html.Div([
                                    html.Div(id='sign-data-table'),
                                ],className="six columns"),
                            ])
                        ]),
                        dcc.Tab(label='Masking Cheque', children=[
                            html.Div([
                                html.H2("Masking View"),
                            ],
                            style={
                                "textAlign": "center",
                                "justify-content": "center",
                                "align-items": "center"}
                            ),  
                            html.Div([
                                html.Div(id='masking-data-upload'),
                            ]),
                        ]),
                        dcc.Tab(label='Listing Cheque Data', children=[
                            html.Div([
                                html.H2("Cheque View"),
                            ],
                            style={
                                "textAlign": "center",
                                "justify-content": "center",
                                "align-items": "center"}
                            ),  
                            html.Div([
                                html.Div(id='extract-cheque-table'),
                            ]),
                        ]),
                    ],id='tab')
                ]) 
            ])

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(path)
    return files

def parse_contents(contents, filename):
    return html.Div([
        html.H2("Image Preview",style = {"color":"blue"}),
        html.H5(filename),
        html.Img(src=contents,style={'height':'50%', 'width':'50%'}),
    ],style={"textAlign": "center",
            "justify-content": "center",
            "align-items": "center"},
    )

@app.callback(dash.dependencies.Output('output-image-data', 'children'),
              dash.dependencies.Input("upload-data", 'contents'),
              dash.dependencies.State("upload-data", 'filename'),)
def update_output(list_of_contents, list_of_names):
    global UPLOADED_FILE_NAME
    UPLOADED_FILE_NAME = list_of_names

    if list_of_contents is not None:
        children = parse_contents(list_of_contents, list_of_names)
        save_file(list_of_names, list_of_contents)
        return children

@app.callback(
    [dash.dependencies.Output("loading-confirm", "children"),],
    [dash.dependencies.Input('submit-provider', 'submit_n_clicks')],
)
def run_process(submit_n_clicks):
    global UPLOADED_FILE_NAME, reduction
    path = os.path.join(UPLOAD_DIRECTORY, UPLOADED_FILE_NAME)
    if submit_n_clicks:
        reduction = process_cheque(path)

@app.callback(dash.dependencies.Output('optimize-data-upload', 'children'),
              dash.dependencies.Input('tab', 'value')
        )
def update_optimize_output(selected_tab):
    global UPLOADED_FILE_NAME, reduction
    filename = UPLOADED_FILE_NAME.split(".")[0]
    path = os.path.join(PROCESS_DIRECTORY, filename + "-optimized.jpeg")
    data_uri = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
    contents = "data:image/png;base64,{0}".format(data_uri)
    return html.Div([
        html.H3("Image Preview",style = {"color":"blue"}),
        html.H5(UPLOADED_FILE_NAME),
        html.Img(src=contents,style={'height':'150%', 'width':'80%'}),
        html.H5(reduction,style = {"color":"blue"}),
        ],style={"textAlign": "center",
                "justify-content": "center",
                "align-items": "center"},
                
        )

def generate_table(dataframe, max_rows=26):
    return html.Table(
        # Header
        [html.Tr([html.Th(col,style = {"color":"blue"}) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    ,style={"textAlign": "center",
                "width": "50%",
               "margin": "auto"})

def update_translated_output():
    global UPLOADED_FILE_NAME, reduction
    filename = UPLOADED_FILE_NAME.split(".")[0]
    path = os.path.join(PROCESS_DIRECTORY, filename + ".json")
    with open(path, 'r') as f:
        response = json.load(f)

    translated = translate_cheque(response)
    print(translated)
    data = []
    for key, value in translated.items():
            data.append({"attribute":key,"value":value["value"],"confidence":value["confidence"]})

    df = pd.DataFrame(data)

    children_table = html.Div([
        html.H3("Data Extracted"),
        generate_table(df),
        ],style={"textAlign": "center",
                "justify-content": "center",
                "align-items": "center"},
                
        )
    return children_table

@app.callback([dash.dependencies.Output("loading-translate", "children"),
            dash.dependencies.Output('extract-data-upload', 'children'),
            dash.dependencies.Output('extract-data-table', 'children')],
            [dash.dependencies.Input('btn-translate', 'n_clicks'),
            dash.dependencies.Input('tab', 'value')]
        )
def update_optimize_output(n_clicks,selected_tab):
    global UPLOADED_FILE_NAME, reduction
    filename = UPLOADED_FILE_NAME.split(".")[0]
    path = os.path.join(PROCESS_DIRECTORY, filename + "-labelled.jpeg")
    data_uri = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
    contents = "data:image/png;base64,{0}".format(data_uri)

    children_image = html.Div([
        html.H3("Image Preview",style = {"color":"blue"}),
        html.Img(src=contents,style={'height':'200%', 'width':'100%'}),
        ],style={"textAlign": "center",
                "justify-content": "center",
                "align-items": "center"},
                
        )
    if n_clicks == 0:
        print("not translating")
        path = os.path.join(PROCESS_DIRECTORY, filename + ".json")
        with open(path, 'r') as f:
            response = json.load(f)
        data = []
        for key, value in response.items():
            if key == 'data_extracted':
                if "identified_labels" in value:
                    for k, d in value["identified_labels"].items():
                        data.append({"attribute":k,"value":d["value"],"confidence":d["confidence"]})

        df = pd.DataFrame(data)

        children_table = html.Div([
            html.H3("Data Extracted",style = {"color":"blue"}),
            generate_table(df),
            ],style={"textAlign": "center",
                    "justify-content": "center",
                    "align-items": "center"},
                    
            )
    else:
        print("translating")
        children_table = update_translated_output()
    
    return "",children_image, children_table

@app.callback(dash.dependencies.Output('masking-data-upload', 'children'),
              dash.dependencies.Input('tab', 'value')
        )
def update_masking_output(selected_tab):
    global UPLOADED_FILE_NAME, reduction
    filename = UPLOADED_FILE_NAME.split(".")[0]
    path = os.path.join(PROCESS_DIRECTORY, filename + "-masked.jpeg")
    data_uri = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
    contents = "data:image/png;base64,{0}".format(data_uri)
    return html.Div([
        html.H3("Image Preview",style = {"color":"blue"}),
        html.H5(UPLOADED_FILE_NAME),
        html.Img(src=contents,style={'height':'50%', 'width':'50%'}),
        ],style={"textAlign": "center",
                "justify-content": "center",
                "align-items": "center"},
                
        )

@app.callback([dash.dependencies.Output('sign-data-upload', 'children'),
             dash.dependencies.Output('sign-data-table', 'children')],
            dash.dependencies.Input('tab', 'value')
        )
def update_sign_output(selected_tab):
    global UPLOADED_FILE_NAME, reduction
    filename = UPLOADED_FILE_NAME.split(".")[0]
    path = os.path.join(PROCESS_DIRECTORY, filename + "-signature.jpeg")
    
    if os.path.exists(path):
        data_uri = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
        contents = "data:image/png;base64,{0}".format(data_uri)

        children_image = html.Div([
            html.H3("Image Preview",style = {"color":"blue"}),
            html.Img(src=contents,style={'height':'200%', 'width':'100%'}),
            ],style={"textAlign": "center",
                    "justify-content": "center",
                    "align-items": "center"},
                    
            )
    else:
        children_image = html.Div([
            html.H3("Image Preview",style = {"color":"blue"}),
            html.H3("No Signature Detected!",style = {"color":"red"}),
            ],style={"textAlign": "center",
                    "justify-content": "center",
                    "align-items": "center"},
                    
            )

    path = os.path.join(PROCESS_DIRECTORY, filename + ".json")
    with open(path, 'r') as f:
        response = json.load(f)
    data = []
    for key, value in response.items():
        if key == "signature_present":
            data.append([key,str(value)])
        if key == "signature_detection_conf":
            data.append([key,value])
        if key == "signatures_verified":
            data.append([key,str(value)])
        if key == "verified_signature_name":
            data.append([key,value])
        if key == "signature_verification_conf":
            data.append([key,value])
        if key == "signature_class":
            data.append([key,value])

    df = pd.DataFrame(data,columns=["Attribute","Value"])

    children_table = html.Div([
        html.H3("Data Extracted",style = {"color":"blue"}),
        generate_table(df),
        ],style={"textAlign": "center",
                "justify-content": "center",
                "align-items": "center"},
                
        )
    return children_image, children_table

@app.callback(dash.dependencies.Output('extract-cheque-table', 'children'),
            dash.dependencies.Input('tab', 'value')
        )
def get_all_items(selected_tab):
    items = get_all()
    df = pd.DataFrame(items)
    table = html.Table(
        # Header
        [html.Tr([html.Th(col,style = {"color":"blue"}) for col in df.columns if col not in ['id','_rid','_self','_etag','_attachments','_ts']]) ] +
        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns if col not in ['id','_rid','_self','_etag','_attachments','_ts']
        ]) for i in range(len(df))]
    ,style={"textAlign": "center",
                "width": "50%",
               "margin": "auto"})
    
    children_table = html.Div([
    html.H3("Cheque Data Extracted",style = {"color":"blue"}),
    table,
    ],style={"textAlign": "center",
            "justify-content": "center",
            "align-items": "center"},            
    )

    return children_table