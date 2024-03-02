import openai

def image_genrate(topic):
        
    response = openai.Image.create(
        prompt=f"""Generate a professional image related to '{topic}'. 
        The image should be high-quality and suitable for use in professional settings. 
        Consider including relevant elements or concepts related to {topic} to convey the desired message. 
        Ensure that the image is visually appealing and aligns with the intended purpose.""",
    )    
    return response
    