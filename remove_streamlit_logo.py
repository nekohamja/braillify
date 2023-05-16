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
                [data-testid="column"] {
                    box-shadow: rgb(0 0 0 / 20%) 0px 5px 1px -1px, rgb(0 0 0 / 14%) 0px 1px 1px 0px, rgb(0 0 0 / 12%) 0px 1px 3px 0px;
                    border-radius: 8px;
                    padding: 5% 5% 5% 5%;
                    background-color: #CADFF3;
                <style>
                    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                    font-size:2rem;
                    }
                </style>   
                } 
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)    

    
