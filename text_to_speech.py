import streamlit as st    
from gtts import gTTS
import io

#this function generates a speech based on the output txt
def text_to_speech(output: str):

    f = io.BytesIO()
    tts = gTTS(text = output, lang ='en')
    tts.write_to_fp(f)
    st.audio(f)




    
 
