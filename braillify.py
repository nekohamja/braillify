import streamlit as st               
from roboflow import Roboflow
from deta import Deta
import PIL
from PIL import Image
import os
from arrange_boxes import sort_letters
from text_to_speech import text_to_speech
from remove_streamlit_logo import remove_streamlit_logo
import numpy as np
import io
import tempfile
import time


remove_streamlit_logo()

#ui elements
st.markdown("<h1 style='text-align: center;'>Braillify</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: grey;'>Optical Braille Alphabet Recognizer (YOLOv5 algorithm)</h1>", unsafe_allow_html=True)
st.text("")
st.text("")
st.markdown("<p style='text-align: center;'>Note: Clean background and proper distance give more accurate results!</p>", unsafe_allow_html=True)
upload_image = st.file_uploader(":camera: Select Photo", type=["png","jpg","jpeg"], label_visibility = 'hidden')
col1, col2 = st.columns(2)
with st.expander("Click me to adjust results!"):
    confidence = float(st.slider("<- More detections │ Less detections ->", 10, 100, 60,)) / 100        
    overlap_threshold = float(st.slider("<- Less Overlapping labels │ More Overlapping labels ->", 10, 100, 25)) / 100 


#yolov5 model using roboflow api
rf = Roboflow(api_key=st.secrets["api_key"]) #add your own api key here
project = rf.workspace().project("braille-final-27-04")
model = project.version(2).model

#deta space cloud drive api (for saving img / audio result)
deta = Deta(st.secrets["deta_key"])  #add your own api key here
uploadedImages = deta.Drive("uploadedImages")

#load the selected image
def load_image(upload):
    image = Image.open(upload).convert("RGB")
    return image
with col1:
    if upload_image is None:
        image = load_image("sample_image.jpg")
        col1.write("Original Image")
        col1.image(image)
    else:
        image = load_image(upload_image)
        col1.write("Original Image")
        col1.image(image)

#generate output text
    def generate_output_text():
        predict_json = predict.json()['predictions']
        text_output = sort_letters(predict_json)
        st.write(text_output)
        return text_output
    
#download button
    def create_download_button():
        btn = st.download_button(
        label="Download Scanned Image",
        data = content,
        file_name = f"image_result.jpg",
        mime = "image/png")

#generate output speech
    def generate_output_speech():
        text_to_speech(text_output)
        
#scan process (if uploaded image is not selected, scan the sample image)
with col2:
    with st.spinner('Processing Image'):
        start_time = time.time()
        if upload_image is None:
            sample_file = 'sample_image.jpg'
            predict = model.predict(sample_file, confidence=confidence, overlap=overlap_threshold)
            def process_image():
                with tempfile.TemporaryDirectory(prefix='braillify_') as tmpdir:
                    file_path = f"{tmpdir}/{sample_file}"
                    predict.save(output_path = f"{tmpdir}/result_{sample_file}")
                    uploadedImages.put(b'uploaded_image.jpg', path = f"{tmpdir}/result_{sample_file}")
                    return predict
            predict = process_image()
            upload = uploadedImages.get('uploaded_image.jpg')
            content = upload.read()
            col2.write("Result")
            col2.image(content)
            upload.close()
            text_output = generate_output_text()
            generate_output_speech()
            create_download_button()
            st.success(f'Success! took {time.time() - start_time:.2f} seconds.', icon="✅")
            st.info("Use the Slider below to adjust detection results.")
        else:
            try:
                def process_image():
                    with tempfile.TemporaryDirectory(prefix='braillify_') as tmpdir:
                        file_path = f"{tmpdir}/{upload_image.name}"
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as img_file:
                            img_file.write(upload_image.getbuffer())
                        predict = model.predict(file_path, confidence=confidence, overlap=overlap_threshold)
                        predict.save(output_path = f"{tmpdir}/result_{upload_image.name}")
                        uploadedImages.put(b'uploaded_image.jpg', path = f"{tmpdir}/result_{upload_image.name}")
                        return predict  
                predict = process_image()
                upload = uploadedImages.get('uploaded_image.jpg')
                content = upload.read()
                col2.write("Result")
                col2.image(content)
                upload.close()
                text_output = generate_output_text()
                generate_output_speech()
                create_download_button()
                st.success(f'Success! took {time.time() - start_time:.2f} seconds.', icon="✅")
                st.info("Use the Slider panel below to adjust the detection results.")
            except Exception as ex:
                st.error("Please try again. Make sure there are visible braille characters!")
                st.error("You may also use the Slider panel to adjust the detection result.") 
