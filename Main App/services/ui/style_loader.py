import os
import streamlit as st
import base64


def load_css(file_path): 
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )


def inject_local_font(font_path, font_family):
    if not os.path.exists(font_path):
        return

    with open(font_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    ext = os.path.splitext(font_path)[1].lstrip(".")
    fmt = {"otf": "opentype"}.get(ext, ext)
    mime = {"otf": "font/otf"}.get(ext, f"font/{ext}")

    st.markdown(
        f"""
        <style>
        @font-face {{
            font-family: '{font_family}';
            src: url(data:{mime};base64,{encoded}) format('{fmt}');
            font-weight: 100 900;
            font-style: normal;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def inject_webrtc_styles():
    st.markdown(
        """
        <style>
        [data-testid="stVideo"] {
            width: 100%;
        }

        [data-testid="stVideo"] video {
            width: 100%;
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )