# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# import re
import openai
import json
# import ast
from django.conf import settings

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

#! Phase 4 Create Article ---------------------------------------------

# def article_generator(article_title, article_subTitles, article_Opening_Keywords , NumOf_ArticleWords , language , Tone_of_voice):
#     article_prompt = f"""
#             Compose a detailed article titled '{article_title}' in {language}, approximately {NumOf_ArticleWords} words in length. Start with an engaging introduction that skillfully weaves in the following keywords: {', '.join(article_Opening_Keywords)}. 

#             The body of the article should be organized under the following subtitles: {'; '.join(article_subTitles)}. Ensure each section seamlessly transitions into the next, maintaining logical coherence and guiding the reader through a comprehensive exploration of digital currencies. 

#             The article should not only adhere to an {Tone_of_voice} tone but also aim to deeply inform and provide a thorough analysis on the evolution, current impact, and future prospects of digital currencies. The narrative should integrate the specified keywords throughout, enriching the reader’s understanding and engagement with the topic.
#             """
#     article_promptTemp = PromptTemplate(
#     input_variables=["text_input"],
#     template="You are a Professional content creator and article Writer:\n\n{text_input}\n\nArticle:")
    
#     chat_openai_gpt3 = ChatOpenAI(temperature=0.5,)
    
#     article_extraction_chain = LLMChain(llm=chat_openai_gpt3, prompt=article_promptTemp)
#     article = article_extraction_chain.run(article_prompt)
    
#     return article

# def full_article(article_title, article_subTitles, article_Opening_Keywords , NumOf_ArticleKeywords , language , Tone_of_voice , outline_list):
    
    
#     article = []
#     outline = []
    
#     try:
        
#         for section in outline_list:

#             para = article_generator(article_title, article_subTitles, article_Opening_Keywords , NumOf_ArticleKeywords , language , Tone_of_voice)
#             outline.append(section)
#             article.append(para)
            
#     except:
#         pass
    
#     return article

def article_generator(idea, outline, section, tone_of_voice , num_ofwords_in_section , language):
    
    if len(outline) == 0:
        article_prompt = f"Generate Catchy Introduction paragraph for my article on {idea} in {language} using the following main point: {section}\nThe tone should be {tone_of_voice} ,  approximately {num_ofwords_in_section} words in length."
        # print('>>>>>>>>>>>>>>>>>>>>>>>>>> outline0')
    else:
        article_prompt = f"Generate well-organized paragraph for my article on {idea}in {language} . approximately {num_ofwords_in_section} words in length. I have already covered: {outline} in the outline. I need help with the following main point: {section}. Please ensure the paragraphs are connected logically and provide a smooth transition between main topics. The tone should be {tone_of_voice}."
        # print('>/>>>>>>>>>>>>>>>>>>>>>>>>> outline1')
    article_promptTemp = PromptTemplate(
    input_variables=["text_input"],
    template="You are a Professional content creator and article Writer:\n\n{text_input}\n\nParagraph:")
    
    chat_openai_gpt3 = ChatOpenAI(temperature=0.5,)
    
    article_extraction_chain = LLMChain(llm=chat_openai_gpt3, prompt=article_promptTemp)
    article = article_extraction_chain.run(article_prompt)
    
    return article

def full_article(idea, outline_list, num_of_words , tone_of_voice , language):
    
    article = []
    outline = []
    num_ofwords_in_section = num_of_words / len(outline_list)
    try:
    
        for section in outline_list:

            para = article_generator(idea, ' '.join(outline), section,  tone_of_voice , num_ofwords_in_section , language)
            outline.append(section)
            article.append(para)
            
            # print( '\n',article,'\n')
            
            
            
    except:
        pass
    
    return article

def convert_response_to_list(response_str):
    # Split the response into lines
    lines = response_str.split('\n')
    # Initialize an empty list to hold the keywords
    keywords_list = []
    
    # Loop through each line
    for line in lines:
        # Remove leading and trailing whitespace
        line = line.strip()
        # Attempt to split the line by the ". " that separates the number from the keyword
        parts = line.split('. ', 1)
        if len(parts) == 2:
            # If successful, take the second part (the keyword phrase) and remove any leading or trailing quotation marks
            keyword = parts[1].strip('\"')
            # Add the cleaned keyword to the list
            keywords_list.append(keyword)
    # print('keywords_list' , keywords_list)
    return keywords_list

def generate_And_Get_KeyWords(topic , num_of_keywords , language):
    try:
        # Define the instruction for the model as a system message
        instruction_message = {
            "role": "system",
             "content": f"""Generate a list of {num_of_keywords} opening keywords or phrases for articles focusing on {topic}, particularly in the field of sustainable energy solutions, in {language} language. These keywords or phrases should target an audience interested in environmental sustainability and may include question starters. """
             #TodoInPrompt Please format your response as a list, similar to ['keyword 1', 'keyword 2']. Ensure the keywords are relevant to the topic and concise.
        }

        # Include the actual text to be processed as a user message 
        text_message = {
            "role": "user",
            "content": topic
        }

        # Combine the instruction and the text into the messages parameter
        gpt3_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[instruction_message, text_message],
            max_tokens=500,
        )

        # Extracting the response
        response = gpt3_response.choices[0].message.content.strip()
        # print(response)
        response = convert_response_to_list(response)
        # Parse the response as JSON
        # response_json = json.loads(response)

    except Exception as e:
        # print(e)
        return "An error occurred while processing the text."

    return response

def generate_And_Get_Titles(topic , Opening_Keywords , num_of_titles , toneOfVoice , language):
    try:
        # Define the instruction for the model as a system message
        instruction_message = {
            "role": "system",
             "content": f"""Generate {num_of_titles} potential article titles for a piece on {topic}, emphasizing sustainable energy solutions, in {language} language. The titles should reflect a {toneOfVoice} tone and resonate with readers interested in environmental sustainability."""
        }

        # Include the actual text to be processed as a user message 
        text_message = {
            "role": "user",
            "content": topic
        }

        # Combine the instruction and the text into the messages parameter
        gpt3_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[instruction_message, text_message],
            max_tokens=500,
        )

        # Extracting the response
        response = gpt3_response.choices[0].message.content.strip()
        # print(response)
        response = convert_response_to_list(response)
        # Parse the response as JSON
        # response_json = json.loads(response)

    except Exception as e:
        # print(e)
        return "An error occurred while processing the text."

    return response

def generate_And_Get_Subtitles(Title, Opening_Keywords, toneOfVoice, language, num_of_points_in_Subtitle):
    try:
        # Define the instruction for the model as a system message
        instruction_message = {
            "role": "system",
            "content": f"""Generate {num_of_points_in_Subtitle} key points for subtitles under the article titled '{Title}', which begins with keywords {Opening_Keywords}. The subtitles should be in {language}, maintain a {toneOfVoice} tone, and each be less than 100 characters. These short subtitles should offer insight or expand on aspects related to the article's main topic, guiding readers through the article's narrative or argument and enhancing their understanding and engagement with the content. Aim for subtitles that are concise yet descriptive."""
        }

        # Include the actual text to be processed as a user message
        text_message = {
            "role": "user",
            "content": Title
        }

        # Combine the instruction and the text into the messages parameter
        gpt3_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[instruction_message, text_message],
            max_tokens=500,  # Adjust max tokens as needed (default 1024)
        )

        # Extracting the response
        response = gpt3_response.choices[0].message.content.strip()
        subtitles = response.split('\n')
        
        # Format each subtitle with a bullet point
        formatted_subtitles = ["- " + subtitle.strip() for subtitle in subtitles if subtitle.strip()]
        
    except Exception as e:
        # print(e)
        return []

    return formatted_subtitles

# def generate_And_Get_Subtitles(Title , Opening_Keywords ,  toneOfVoice , language ,  num_of_points_in_Subtitle ):
#     openai.api_key = settings.OPENAI_API_KEY
#     try:
#         # Define the instruction for the model as a system message
#         instruction_message = {
#     "role": "system",
#     "content": f"""Generate {num_of_points_in_Subtitle} key points for subtitles under the article titled '{Title}', which begins with keywords {Opening_Keywords}. The subtitles should be in {language} and maintain a {toneOfVoice} tone, offering insight or expanding on aspects related to the article's main topic. These points should guide readers through the article's narrative or argument, enhancing their understanding and engagement with the content."""
# }


#         # Include the actual text to be processed as a user message 
#         text_message = {
#             "role": "user",
#             "content": Title
#         }

#         # Combine the instruction and the text into the messages parameter
#         gpt3_response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo-16k",
#             messages=[instruction_message, text_message ],
#               # Adjust max tokens as needed (default 1024)
            
#         )

#         # Extracting the response
#         response = gpt3_response.choices[0].message.content.strip()
        
#         # response = convert_response_to_list(response)
#         # Parse the response as JSON
#         # response_json = json.loads(response)
        
#     except Exception as e:
#         print(e)
#         return "An error occurred while processing the text."

#     return response


# for i in range(3):
# print(generate_And_Get_Subtitles(Title = 'Python' , Opening_Keywords = ["Unleashing the Power of Python: How this Programming Language is Revolutionizing Sustainable Energy Solutions"]\
#     ,  toneOfVoice  = 'exciting', language = 'en' ,  num_of_points_in_Subtitle = '3' ))
# print()
    
#         # Combine the instruction and the text into the messages parameter
#         gpt3_response = openai.Completion.create(
#             engine="text-davinci",  # GPT-3 engine identifier
#             prompt=instruction_message["content"] + "\n" + text_message["content"],
#             max_tokens=1024,  # Adjust max tokens as needed (default 1024)
#             n=1,  # Generate only 1 response
#             stop=None,  # No explicit stop sequence needed
#             temperature=0.7,  # Control creativity (0: deterministic, 1: maximally random)
#         )
