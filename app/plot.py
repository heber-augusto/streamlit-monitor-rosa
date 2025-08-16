import plotly.express as px

def plot_line(data, y_column_name, metrics_selector):
    fig = px.line(
        data,
        x='data',
        y=y_column_name,
        color='estadiamento',
        symbol='estadiamento'
    )
    fig.update_layout(
        yaxis_title=metrics_selector,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0.01
        )
    )
    return fig
