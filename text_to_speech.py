import streamlit as st    
from deta import Deta
from gtts import gTTS
import io


#deta space cloud drive (for saving img / audio result)
deta = Deta(st.secrets["deta_key"])  #add your own api key here
uploadedImages = deta.Drive("uploadedImages")

#this function generates a speech based on the output txt
def text_to_speech(output: str):

    f = io.BytesIO()
    tts = gTTS(text = output, lang ='en')
    tts.write_to_fp(f)
    st.audio(f)




    
 