import os
import uuid
from PIL import Image

def save_uploaded_image(uploaded_file):
    ext = uploaded_file.name.split('.')[-1]
    save_path = f"user_image_{uuid.uuid4()}.{ext}"
    image = Image.open(uploaded_file)
    image.save(save_path)
    return save_path