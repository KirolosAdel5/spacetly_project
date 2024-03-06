# import openai
from django.conf import settings 
# from PIL import Image
import requests
# from io import BytesIO
import uuid
import os
# from django.core.files import File
# from urllib.parse import urljoin
import base64
from langdetect import detect
from googletrans import Translator, LANGUAGES
api_key  = os.environ.get('STABILITY_API_KEY')

def generate_unique_id():
    unique_id = uuid.uuid4()
    return str(unique_id)

def detect_language(text):
    try:
        language = detect(text)
        return language
    except:
        return "Unknown"
    
def translate_to_english(text):
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return translation.text
    

url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
api_key  = os.environ.get('STABILITY_API_KEY')
def image_genrate(topic):
    input_language = detect_language(topic)
    if input_language.lower() != 'en':
        topic = translate_to_english(topic)
        
    prompt=f"""Generate a professional image related to '{topic}' . 
        The image should be high-quality and suitable for use in professional settings. 
        Consider including relevant elements or concepts related to {topic} to convey the desired message. 
        Ensure that the image is visually appealing and aligns with the intended purpose."""
    
    body = {
    "steps": 40,
    "width": 1024,
    "height": 1024,
    "seed": 0,
    "cfg_scale": 5,
    "samples": 1,
    "text_prompts": [
        {
        "text": prompt,
        "weight": 1
        },
        {
        "text": "blurry, bad",
        "weight": -1
        }
    ],
    }

    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-co4Tz2huTMAYKj7dAe8lEYgZNTq9LJwZ9s8Riqjq873fN1or",
    }

    response = requests.post(
    url,
    headers=headers,
    json=body
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    dir_path = os.path.join(settings.MEDIA_ROOT, 'gene')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


    unique_id = generate_unique_id()
    filename = f'{unique_id}.png'
    
    # Assume only one image is generated
    image = data["artifacts"][0]
    file_path = os.path.join(dir_path, f'{filename}_{image["seed"]}.png')

    # Write the image data to the file
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(image["base64"]))

    # Construct the URL using Django settings
    media_url = settings.MEDIA_URL
    image_url = f'{media_url}gene/{filename}_{image["seed"]}.png'

    return image_url


# ----------------------------------------------------------------  --------------------------------
# def resize(image_url, shape):
#     image_response = requests.get(image_url)
#     image = Image.open(BytesIO(image_response.content))
#     resized_image = image.resize((int(shape[0]), int(shape[1])))  
    
#     unique_id = generate_unique_id()
#     filename = f'{unique_id}.png'
#     dir = os.path.join(settings.MEDIA_ROOT, 'gene')
#     if not os.path.exists(dir):
#         os.makedirs(dir)
    
#     file_path = os.path.join(dir, filename)
#     resized_image.save(file_path)
    
#     return unique_id

# def image_genrate(topic, style, num_Of_Images, shape):
#     shape = shape.split("X")
    
#     images_data = {}
    
#     response = openai.Image.create(
#         model="dall-e-3",
#         prompt=f"""Generate a professional image related to '{topic}' in a '{style}' style. 
#         The image should be high-quality and suitable for use in professional settings. 
#         Consider including relevant elements or concepts related to {topic} to convey the desired message. 
#         Ensure that the image is visually appealing and aligns with the intended purpose.""",
#         n=num_Of_Images  # the number of images
#     )
    
#     for image_data in response['data']:
#         image_url = image_data['url']
#         unique_id = resize(image_url, shape)
#         # Construct the local URL relative to MEDIA_URL
#         relative_path = f'{settings.MEDIA_URL}/gene/{unique_id}.png'
#         local_url = urljoin(settings.MEDIA_URL, relative_path)
#         images_data[unique_id] = local_url
        
#     return images_data
    
# # print(image_genrate('cat' , 'relastic' , 3 , '200X200'))

# # D:\spactly\myenv\media\gene\b428bde3-61c8-4b1a-88a4-78b47ba63542.png