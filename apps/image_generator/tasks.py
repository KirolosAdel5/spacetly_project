import openai
from django.conf import settings 
from PIL import Image
import requests
from io import BytesIO
import uuid
import os
from django.core.files import File
from urllib.parse import urljoin

def generate_unique_id():
    unique_id = uuid.uuid4()
    return str(unique_id)

def resize(image_url, shape):
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))
    resized_image = image.resize((int(shape[0]), int(shape[1])))  
    
    unique_id = generate_unique_id()
    filename = f'{unique_id}.png'
    dir = os.path.join(settings.MEDIA_ROOT, 'gene')
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    file_path = os.path.join(dir, filename)
    resized_image.save(file_path)
    
    return unique_id

def image_genrate(topic, style, num_Of_Images, shape):
    shape = shape.split("X")
    
    images_data = {}
    
    response = openai.Image.create(
        model="dall-e-3",
        prompt=f"""Generate a professional image related to '{topic}' in a '{style}' style. 
        The image should be high-quality and suitable for use in professional settings. 
        Consider including relevant elements or concepts related to {topic} to convey the desired message. 
        Ensure that the image is visually appealing and aligns with the intended purpose.""",
        n=num_Of_Images  # the number of images
    )
    
    for image_data in response['data']:
        image_url = image_data['url']
        unique_id = resize(image_url, shape)
        # Construct the local URL relative to MEDIA_URL
        relative_path = f'{settings.MEDIA_URL}/gene/{unique_id}.png'
        local_url = urljoin(settings.MEDIA_URL, relative_path)
        images_data[unique_id] = local_url
        
    return images_data
    
# print(image_genrate('cat' , 'relastic' , 3 , '200X200'))

# D:\spactly\myenv\media\gene\b428bde3-61c8-4b1a-88a4-78b47ba63542.png