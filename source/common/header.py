import dash_html_components as html
import dash_core_components as dcc


header_layout = html.Div([
	html.Div([
		html.Div([
			html.H2(children="Automated Cheque Processing"),
		], className="six columns",style={'color':'white'}),
	],className="row",
	style={'background-color':'#212121',
		"textAlign": "center",
		"justify-content": "center",
		"align-items": "center"})
])
