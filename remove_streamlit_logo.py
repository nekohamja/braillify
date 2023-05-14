import streamlit as st   

def remove_streamlit_logo():
    #remove hamburger menu and streamlit logo
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {
                    visibility: hidden;
                    }
                footer:after {
                    content:' '; 
                    visibility: visible;
                    display: block;
                    position: relative;
                    #background-color: black;
                    padding: 5px;
                    top: 2px;
                }
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)    