# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload for slider range
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a Dash app
app = dash.Dash(__name__)

# Create dropdown options
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36',
                                                       'font-size': 40}),
    # Dropdown
    dcc.Dropdown(id='site-dropdown',
                 options=site_options,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Payload slider
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),
    html.Br(),

    # Scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        df.columns = ['Launch Site', 'Successes']
        fig = px.pie(df, values='Successes', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = df['class'].value_counts().reset_index()
        counts.columns = ['Outcome', 'Count']
        counts['Outcome'] = counts['Outcome'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Success vs Failure for site {entered_site}')
    return fig

# Callback for scatter plot
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version',
                         title='Correlation Between Payload and Success for All Sites')
    else:
        df = df[df['Launch Site'] == entered_site]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version',
                         title=f'Payload vs Success for site {entered_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
