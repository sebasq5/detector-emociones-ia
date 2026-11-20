from collections import Counter

import plotly.graph_objects as go

from src.utils import EMOTIONS, percentage


def horizontal_chart(items, axis_title):
    labels, values = zip(*items)
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=[EMOTIONS[label][1] for label in labels],
        text=[percentage(value) for value in values], textposition="outside",
        cliponaxis=False, hovertemplate="%{y}<br>%{text}<extra></extra>",
    ))
    fig.update_layout(
        height=318, margin=dict(l=0, r=48, t=8, b=48),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.42,
        xaxis=dict(title=axis_title, range=[0, 1.04], tickformat=".0%", dtick=0.25),
        yaxis=dict(autorange="reversed", categoryorder="array", categoryarray=list(labels)),
    )
    return fig


def probability_chart(result):
    items = sorted(result["probabilities"].items(), key=lambda item: item[1], reverse=True)
    return horizontal_chart(items, "Probabilidad")


def distribution_chart(results):
    counts = Counter(result["emotion"] for result in results)
    items = [(emotion, counts[emotion] / len(results)) for emotion in EMOTIONS]
    figure = horizontal_chart(sorted(items, key=lambda item: item[1], reverse=True), "Proporción de textos")
    figure.data[0].customdata = [counts[label] for label in figure.data[0].y]
    figure.data[0].hovertemplate = "%{y}<br>%{customdata} textos · %{text}<extra></extra>"
    return figure
