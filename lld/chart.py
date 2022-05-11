import json

from flask import current_app, g

import plotly
import plotly.express as px


def make_chart(df, sensor, var):

    # TODO determine appropriate plot from sensor type

    # Create pond sensor plot
    # TODO read in units from metadata section and display in title/y axis label
    fig = px.line(df, x=df.index, y=var, title=f'{sensor["display_name"]}: {var}')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
