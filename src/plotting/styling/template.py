import plotly.io as pio


def defineTemplate():
    t = pio.templates['plotly']

    # paper colour, plot bg colour, font colour, font family
    t.update(
        layout=dict(
            paper_bgcolor='rgba(255, 255, 255, 1.0)',
            plot_bgcolor='rgba(255, 255, 255, 0.0)',
            font_color='black',
            font_family='Helvetica',
        )
    )

    # legend styling
    t.update(
        layout_legend=dict(
            bgcolor='rgba(255,255,255,1.0)',
            bordercolor='black',
            borderwidth=2,
        ),
    )

    # axis styling
    t.update(
        layout={axis: dict(
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            zeroline=False,
            mirror=True,
            ticks='outside',
        ) for axis in ['xaxis', 'yaxis']}
    )

    return t
