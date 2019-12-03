# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
from plotly.graph_objs import *
#from heading import title

# Multi-dropdown options
from controls import  GEOGRAPHIC, SUBJECTS, WELL_COLORS

#years
style = {'transform': 'rotate(90deg) translateX(25%) translateY(75%)'}
years = [i for i in range (2000, 2019)]
y_marks = {}
for year in years:
    y_marks[year] = {'label':str(year), 'style':style}
#print(y_marks)


# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

geographic_options = [
    {"label": str(GEOGRAPHIC[geo]), "value": str(geo)}
    for geo in GEOGRAPHIC
]

subjects_options = [
    {"label": str(SUBJECTS[subject]), "value": str(subject)}
    for subject in SUBJECTS
]

# Load data


# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="dark",
        center=dict(lon=-74.2973328, lat=4.570868),
        zoom=4,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("ds4A-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Empowering Education in Colombia",
                                    style={"margin-bottom": "0px"},
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                    style ={'display':'block'}
                ),
                
                html.Div(
                    [
                        dcc.Tabs(id="tabs-example", value='tab-1-example', children=[
                        dcc.Tab(label='Dashboard', value='tab-1-example'),
                        dcc.Tab(label='Simulator', value='tab-2-example'),
                    ], colors={
                        "border": "white",
                        "primary": "white",
                        "background": "Gainsboro"
                    }),],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                 
                html.Div(
                    [
                        html.H5(
                            "Filters:",
                            className="control_label",
                        ),
                        html.P(
                            "Date:",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=2000,
                            max=2018,
                            value=[2005, 2007],
                            marks = y_marks,
                            className="dcc_control",
                        ),

                        html.Br(),
                        html.Br(),
                        

                        html.P("Geographic:", className="control_label"),

                        dcc.Dropdown(
                            id="GEOGRAPHIC",
                            options=geographic_options,
                            multi=False,
                            value=list(GEOGRAPHIC.keys()),
                            className="dcc_control",
                        ),

                        html.P("Subjects:", className="control_label"),
                        dcc.Dropdown(
                            id="SUBJECTS",
                            options=subjects_options,
                            multi=True,
                            value=list(SUBJECTS.keys()),
                            className="dcc_control",
                        ),

                        html.P("Visualization Type:", className="control_label"),
                        dcc.RadioItems(
                            id="well_type_selector",
                            options=[
                                {"label": "Heatmap ", "value": "all"},
                                {"label": "Best areas ", "value": "productive"},
                                {"label": "Problematic areas ", "value": "custom"},
                            ],
                            value="productive",
                            className="dcc_control",
                        ),

                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.P("Average")],
                                    id="media",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Maximum")],
                                    id="max",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Minimun")],
                                    id="min",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="waterText"), html.P("Standard Deviation")],
                                    id="std",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="main_graph")],
                            id="pretty_container seven columns",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="second_row_left_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="second_row_right_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(

                    [dcc.Graph(id="third_row_left_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="third_row_right_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


@app.callback(
    Output("main_graph", "figure"),
    [
        Input("GEOGRAPHIC", "value"),
        Input("SUBJECTS", "value"),
        Input("year_slider", "value"),
    ],
    [State("main_graph", "relayoutData")],
)
def make_main_figure(
    GEOGRAPHIC, SUBJECTS, year_slider, main_graph_layout
):

    #dff = filter_dataframe(df, GEOGRAPHIC, SUBJECTS, year_slider)
    figure={ 
        'data': [go.Scattermapbox()],
        'layout': layout
        }

    return figure



# Main
if __name__ == "__main__":
    app.run_server(debug=True)
