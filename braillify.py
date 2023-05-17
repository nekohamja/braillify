import streamlit as st               
from roboflow import Roboflow
from deta import Deta
from ultralytics import YOLO
import cv2
import PIL
from PIL import Image
import os
from yolov5_arrange_boxes import sort_letters
from yolov8_arrange_boxes import convert_to_braille_unicode, parse_xywh_and_class
from text_to_speech import text_to_speech
from remove_streamlit_logo import remove_streamlit_logo
import numpy as np
import io
import tempfile
import time


remove_streamlit_logo()

#ui elements
st.markdown("<h1 style='text-align: center;'>Braillify</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: grey;'>Grade 1 Braille Alphabet Recognizer</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: grey;'>(YOLOv5 & YOLOv8 algorithm)</h1>", unsafe_allow_html=True)
st.text("")
st.text("")
st.markdown("<p style='text-align: center;'>Note: Limited to processing words and phrases only.</p>", unsafe_allow_html=True)
upload_image = st.file_uploader(":camera: Select Photo", type=["png","jpg","jpeg"], label_visibility = 'hidden')
col1 = st.container()
col2, col3 = st.columns(2)
with st.expander("Click me to adjust results!"):
    confidence = float(st.slider(":arrow_backward: More detections │ Less detections :arrow_forward:", 10, 100, 60,)) / 100        
    overlap_threshold = float(st.slider(":arrow_backward: Less Overlapping labels │ More Overlapping labels :arrow_forward:", 10, 100, 25)) / 100 


#yolov5 model using roboflow api
@st.cache_resource()
def load_model():
    rf = Roboflow(api_key=st.secrets["api_key"]) #add your own api key here
    project = rf.workspace().project("braille-final-27-04")
    return project.version(2).model
yolov5 = load_model()
#deta space cloud drive api (for saving img / audio result of yolov5)
deta = Deta(st.secrets["deta_key"])  #add your own api key here
uploadedImages = deta.Drive("uploadedImages")

#yolov8 model
@st.cache_resource()
def load_model_2():
    return YOLO("yolov8_braille.pt")
try:
    yolov8 = load_model_2()
    yolov8.overrides["conf"] = confidence 
    yolov8.overrides["iou"] = overlap_threshold
    yolov8.overrides["agnostic_nms"] = False 
    yolov8.overrides["max_det"] = 1000
except Exception as ex:
    st.error("Unable to load model. Try refreshing your browser.")


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


        
#YOLOv5 scan process
with col2:
    #generate output text
    col2.empty()
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

    with st.spinner('YOLOv5 algorithm running...'):
        start_time = time.time()
        if upload_image is None:
            sample_file = 'sample_image.jpg'
            predict = yolov5.predict(sample_file, confidence=confidence, overlap=overlap_threshold)
            def process_image():
                with tempfile.TemporaryDirectory(prefix='braillify_') as tmpdir:
                    file_path = f"{tmpdir}/{sample_file}"
                    predict.save(output_path = f"{tmpdir}/result_{sample_file}")
                    url = f"uploaded_image_{sample_file}"
                    uploadedImages.put(bytes(url, encoding = 'utf-8'), path = f"{tmpdir}/result_{sample_file}")
                    return predict
            predict = process_image()
            upload = uploadedImages.get(f"uploaded_image_{sample_file}")
            content = upload.read()
            col2.write("YOLOv5 algorithm result: ")
            col2.image(content)
            upload.close()
            text_output = generate_output_text()
            generate_output_speech()
            create_download_button()
            st.success(f'Success! took {time.time() - start_time:.2f} seconds.', icon="✅")
        else:
            try:
                def process_image():
                    with tempfile.TemporaryDirectory(prefix='braillify_') as tmpdir:
                        file_path = f"{tmpdir}/{upload_image.name}"
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as img_file:
                            img_file.write(upload_image.getbuffer())
                        predict = yolov5.predict(file_path, confidence=confidence, overlap=overlap_threshold)
                        predict.save(output_path = f"{tmpdir}/result_{upload_image.name}")
                        url = f"uploaded_image_{upload_image.name}"
                        uploadedImages.put(bytes(url, encoding = 'utf-8'), path = f"{tmpdir}/result_{upload_image.name}")
                        return predict  
                predict = process_image()
                upload = uploadedImages.get(f"uploaded_image_{upload_image.name}")
                content = upload.read()
                col2.write("YOLOv5 algorithm result: ")
                col2.image(content)
                upload.close()
                text_output = generate_output_text()
                generate_output_speech()
                create_download_button()
                st.success(f'Success! took {time.time() - start_time:.2f} seconds.', icon="✅")
            except Exception as ex:
                st.error("Please try again. Make sure there are visible braille characters or adjust the detection using the slider below.")

#YOLOv8 scan process
with col3:
    col3.empty()
    #download button
    def create_download_button():
        img = Image.fromarray(res_plotted)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        byte_im = buf.getvalue()
        btn = st.download_button(
        label="Download Scanned Image",
        data = byte_im,
        file_name = f"image_result.jpg",
        mime = "image/png")

    #generate output speech
    def generate_output_speech():
        text_to_speech(str_left_to_right)


    with st.spinner('YOLOv8 algorithm running...'):
        start_timer = time.time()
        try:
            if upload_image is None:
                predict = yolov8.predict('sample_image.jpg', exist_ok=True, conf=confidence)
            else:
                def process_image():
                    with tempfile.TemporaryDirectory(prefix='braillify_') as tmpdir:
                        file_path = f"{tmpdir}/{upload_image.name}"
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as img_file:
                            img_file.write(upload_image.getbuffer())
                        predict = yolov8.predict(file_path, exist_ok=True, conf=confidence)
                        return predict  
                predict = process_image()
            res_plotted = predict[0].plot()[:, :, ::-1]
            col3.write("YOLOv8 algorithm result: ")
            col3.image(res_plotted)
            boxes = predict[0].boxes     
            list_boxes = parse_xywh_and_class(boxes)
            for box_line in list_boxes:
                str_left_to_right = ""
                box_classes = box_line[:, -1]
                for each_class in box_classes:
                    str_left_to_right += convert_to_braille_unicode(
                    yolov8.names[int(each_class)]
                )
                st.write(str_left_to_right)
            generate_output_speech()
            create_download_button()
            st.success(f'Success! took {time.time() - start_timer:.2f} seconds.', icon="✅")
        except Exception as ex:
            st.error("Please try again. Make sure there are visible braille characters or adjust the detection using the slider below.")
        
