import openai
from django.conf import settings
import os
import uuid
import requests
from urllib.parse import urljoin

# Set your API key

def generate_unique_id():
    unique_id = uuid.uuid4()
    return str(unique_id)

def save_image_from_url(image_url):
    """
    Save an image from the given URL to the server's media directory.
    """
    # Generate a unique ID for the image name
    unique_id = generate_unique_id()
    filename = f"{unique_id}.png"
    
    # Ensure the media directory exists
    media_dir = os.path.join(settings.MEDIA_ROOT, "gene")
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Download the image from the URL
    image_response = requests.get(image_url)
    image_data = image_response.content

    # Save the image to the media directory
    file_path = os.path.join(media_dir, filename)
    with open(file_path, "wb") as f:
        f.write(image_data)

    # Return the unique ID of the saved image
    return unique_id

def image_genrate(topic):
    """
    Generate an image related to the given topic using the OpenAI API.
    Save the image to the server's media directory defined in settings and return its URL.
    """
    response = openai.Image.create(
        prompt=f"""Generate a professional image related to '{topic}'. 
        The image should be high-quality and suitable for use in professional settings. 
        Consider including relevant elements or concepts related to {topic} to convey the desired message. 
        Ensure that the image is visually appealing and aligns with the intended purpose."""
    )
    
    unique_id = save_image_from_url(response['data'][0]['url'])
    relative_path = f"gene/{unique_id}.png"
    full_url = settings.MEDIA_URL + relative_path
    return full_url