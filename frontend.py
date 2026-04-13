import streamlit as st
import time
import pandas as pd
import numpy as np
import os
import requests
import openai
import json
import re
import datetime
import json
import backend.functions as back

st.set_page_config(
    page_title="Way Academy - Demo chatbot", 
    page_icon="🤖"
)

st.title("Way  Academy - Demo chatbot")
st.info(
    """AI chatbot course deliverable demonstration"""
)

        
### Chat Session Control

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message.keys():
            st.markdown(message["output"])
            
    
if "waiting" not in st.session_state:
    st.session_state.waiting = False
    

### Chat user prompt & response generation

prompt = st.chat_input("Танд юугаар туслах вэ?", disabled=st.session_state.waiting)

if prompt:
    # Disable input while waiting for response
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "output": prompt})
    
    st.session_state.waiting = True
    st.rerun()

if st.session_state.waiting:
    last_prompt = st.session_state.messages[-1]["output"] if st.session_state.messages else prompt
    
    with st.spinner("Хариу бичиж байна..."):
        answer = {}
        answer['response'] = back.handle_user_query(last_prompt)

    st.chat_message("assistant").markdown(answer['response'])
    st.session_state.messages.append({"role": "assistant", "output": answer['response']})

    # Re-enable input
    st.session_state.waiting = False
    st.rerun()
