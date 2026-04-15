import streamlit as st
import time
import pandas as pd
import numpy as np
import os
import requests
import json
import re
import datetime
import backend.functions as back

st.set_page_config(
    page_title="Way Academy - Demo chatbot",
    page_icon="🤖"
)
st.title("Way Academy - Demo chatbot")
st.info("AI chatbot course deliverable demonstration")


### ── Helpers ──────────────────────────────────────────────────────────────

def render_message(message: dict):
    """Render a single stored message (text, DataFrame, or mixed)."""
    output = message.get("output")
    df     = message.get("dataframe")        # stored DataFrame, if any

    if isinstance(output, str) and output:
        st.markdown(output)

    if df is not None:
        render_dataframe(df)


def render_dataframe(df: pd.DataFrame):
    """Render a DataFrame as a styled, interactive table."""
    # ── Numeric formatting: strip thousands-separator strings if present ──
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = df[col].astype(str).str.replace(",", "", regex=False).astype(float)
            except (ValueError, TypeError):
                pass

    st.markdown("**📊 Exchange rates**")

    # Transpose so currencies become rows — much easier to read
    if "RATE_DATE" in df.columns:
        date_val = df["RATE_DATE"].iloc[0]
        st.caption(f"Rate date: **{date_val}**")
        display = (
            df.drop(columns=["RATE_DATE"])
              .T
              .reset_index()
        )
        display.columns = ["Currency", "Rate (MNT)"]
        display["Rate (MNT)"] = pd.to_numeric(display["Rate (MNT)"], errors="coerce")
    else:
        display = df.copy()

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rate (MNT)": st.column_config.NumberColumn(
                "Rate (MNT)",
                format="%.2f",
            )
        },
    )


### ── Session state init ───────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "waiting" not in st.session_state:
    st.session_state.waiting = False


### ── Replay history ───────────────────────────────────────────────────────

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message)


### ── Input & response ─────────────────────────────────────────────────────

prompt = st.chat_input("Танд юугаар туслах вэ?", disabled=st.session_state.waiting)

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "output": prompt})
    st.session_state.waiting = True
    st.rerun()

if st.session_state.waiting:
    last_prompt = (
        st.session_state.messages[-1]["output"]
        if st.session_state.messages
        else ""
    )

    with st.spinner("Хариу бичиж байна..."):
        result = back.handle_user_query(last_prompt)

    # ── Detect result type ────────────────────────────────────────────────
    stored: dict = {"role": "assistant"}

    if isinstance(result, pd.DataFrame):
        # Backend returned a DataFrame directly
        stored["output"] = ""
        stored["dataframe"] = result

    elif isinstance(result, dict):
        # Backend returned a dict — could be {"response": "...", "data": df}
        stored["output"] = result.get("response", "")
        df_candidate = result.get("data") or result.get("dataframe")
        if isinstance(df_candidate, pd.DataFrame):
            stored["dataframe"] = df_candidate

    else:
        # Plain string / anything else
        stored["output"] = str(result)

    with st.chat_message("assistant"):
        render_message(stored)

    st.session_state.messages.append(stored)
    st.session_state.waiting = False
    st.rerun()