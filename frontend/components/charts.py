"""
EduPath AI - Streamlit Visual Charts & Plotly Visualizations
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

def create_gauge_chart(value: float, title: str = "Completion Progress") -> go.Figure:
    """Create a modern circular gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 20, 'color': '#1E293B'}},
        number={'suffix': "%", 'font': {'size': 26, 'color': '#2563EB', 'family': 'Arial'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#2563EB"},
            'bgcolor': "#F1F5F9",
            'borderwidth': 2,
            'bordercolor': "#CBD5E1",
            'steps': [
                {'range': [0, 40], 'color': '#FEE2E2'},
                {'range': [40, 75], 'color': '#FEF3C7'},
                {'range': [75, 100], 'color': '#DCFCE7'}
            ]
        }
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1E293B")
    )
    return fig

def create_skills_radar_chart(categories: Dict[str, int]) -> go.Figure:
    """Create a polar radar chart representing student skill distribution."""
    labels = list(categories.keys())
    values = list(categories.values())
    if not labels:
        labels = ["Technical", "Soft Skills", "Domain"]
        values = [0, 0, 0]

    # Close loop
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.25)',
        line=dict(color='#2563EB', width=2),
        name='Skill Competence'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(max(values, default=5) + 2, 5)])
        ),
        showlegend=False,
        height=300,
        margin=dict(l=30, r=30, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_recommendation_bar_chart(recommendations: List[Dict[str, Any]]) -> go.Figure:
    """Create a horizontal bar chart of career match percentages."""
    if not recommendations:
        return go.Figure()

    roles = [r.get("role_title", "Role") for r in recommendations][:5]
    scores = [r.get("match_percentage", 0.0) for r in recommendations][:5]

    fig = go.Figure(go.Bar(
        x=scores,
        y=roles,
        orientation='h',
        marker=dict(
            color=scores,
            colorscale='Blues',
            line=dict(color='#1E40AF', width=1.5)
        ),
        text=[f"{s}%" for s in scores],
        textposition='outside'
    ))

    fig.update_layout(
        title="Career Compatibility Match (%)",
        xaxis=dict(range=[0, 105], title="Match Percentage"),
        yaxis=dict(autorange="reversed"),
        height=280,
        margin=dict(l=20, r=40, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig
