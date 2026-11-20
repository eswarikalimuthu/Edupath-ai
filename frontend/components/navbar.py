"""
EduPath AI - Sidebar & Global Styles
"""

import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }
            
            /* Main container padding */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1200px;
            }
            
            /* Sidebar customization */
            section[data-testid="stSidebar"] {
                background-color: #F8FAFC;
                border-right: 1px solid #E2E8F0;
            }
            
            /* Buttons */
            .stButton>button {
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.2s ease;
            }
            
            /* Data tables & metrics */
            div[data-testid="stMetricValue"] {
                font-size: 26px;
                font-weight: 700;
            }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    apply_custom_styles()
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                <span style="font-size: 32px;">🎓</span>
                <div>
                    <h3 style="margin: 0; font-weight: 800; color: #1E293B; font-size: 20px;">EduPath AI</h3>
                    <span style="font-size: 11px; color: #64748B; font-weight: 600; letter-spacing: 0.5px;">SIH25094 PLATFORM</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        user = st.session_state.get("user")
        if user:
            st.success(f"👤 Logged in as **{user.get('username')}**")
            st.caption(f"Role: `{user.get('role', 'student').upper()}`")
            if st.button("🚪 Log Out", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.info("👋 Welcome, Guest! Please sign in or register to unlock AI roadmaps and recommendations.")
            
        st.divider()
        st.markdown(
            """
            <div style="font-size: 12px; color: #94A3B8; line-height: 1.6;">
                <strong>Core Features:</strong><br/>
                • 5 LangGraph Autonomous Agents<br/>
                • Dense + BM25 Hybrid RAG<br/>
                • Verifiable Source Citations<br/>
                • Multi-Stage Learning Roadmaps
            </div>
            """,
            unsafe_allow_html=True
        )
