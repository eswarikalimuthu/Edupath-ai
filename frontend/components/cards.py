"""
EduPath AI - Frontend Card & UI Utility Components
"""

import streamlit as st
from typing import Any

def render_metric_card(title: str, value: Any, subtitle: str = "", icon: str = "📌", color_border: str = "#2563EB"):
    st.markdown(
        f"""
        <div style="
            background: #FFFFFF;
            border-radius: 12px;
            padding: 18px 22px;
            border-left: 5px solid {color_border};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 15px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 14px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">{title}</span>
                <span style="font-size: 22px;">{icon}</span>
            </div>
            <div style="font-size: 28px; font-weight: 700; color: #0F172A; margin: 8px 0 4px 0;">{value}</div>
            <div style="font-size: 13px; color: #94A3B8;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_header(title: str, subtitle: str = "", badge: str = None):
    badge_html = f'<span style="background: #EFF6FF; color: #2563EB; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; border: 1px solid #BFDBFE; vertical-align: middle; margin-left: 10px;">{badge}</span>' if badge else ''
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 30px; font-weight: 800; color: #0F172A; margin-bottom: 6px;">{title}{badge_html}</h1>
            <p style="font-size: 15px; color: #64748B; margin-top: 0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
