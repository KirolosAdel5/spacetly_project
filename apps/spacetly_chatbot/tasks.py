from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
import openai
from dotenv import load_dotenv, find_dotenv
import os
from django.conf import settings
import dotenv
import time
# from .chat_image import image_genrate

dotenv.load_dotenv()
google_gemini = ChatGoogleGenerativeAI(model="gemini-pro",
                              tempreature = 0.5,
                              convert_system_message_to_human=True
                              ,)

chat_openai_gpt3 = ChatOpenAI(temperature=0.5,)
chat_openai_gpt4 = ChatOpenAI(temperature=0.5, model='gpt-4',)

def define_memory(k=7):
    
    '''
    desc:
    
        define_memory() is a fuction can be used to instantiate the memory. 
        We need the memory to store the previous conversation between the User and the AI
    '''
    
    '''
    Params and args:
    
        k [Optional=7]: k is the number of conversation chat history that are saved in the memory.
    '''
    
    '''
    return:
    
         This function returns Memory as Object. 
    '''
    
    memory = ConversationBufferWindowMemory(k=k)
    
    return memory

memory = define_memory()


def define_conv_chain(memory, llm=google_gemini):
    
     
    '''
    desc:
    
        define_conv_chain() is a fuction can be used to instantiate the conversational chain. 
        conversational chain used to connect between the LLM and the memory
    '''
    
    '''
    Params and args:
    
        memory [Required]: Memory to store chat history.
        llm [Optional=google_chat_palm]: The LLM.
    '''
    
    '''
    return:
    
         This function Conversation chain as object that can be used for conversation.
    '''
    
    conv_chain = ConversationChain(
        llm=llm,
        memory=memory
    )
    
    return conv_chain


def chat(conv_chain, message):

    ans = conv_chain.predict(input=message)
    return ans
start = time.time() 
print(chat(define_conv_chain(memory, chat_openai_gpt3), "عرفني بنفسك"))
end = time.time()
print(end - start)
# def chat_logic(message_list, ai_model):
#     # Your existing logic to initialize the conversation chain and interact with the chat model
#     last_user_message = message_list[-1]["content"]
#     response = None
    
#     if ai_model == 'ChatGPT':
#         chat_model = define_conv_chain(memory, chat_openai_gpt3)
#     elif ai_model == 'GPT4':
#         chat_model = define_conv_chain(memory, chat_openai_gpt4)
#     elif ai_model == 'Google PalM 2':
#         chat_model = define_conv_chain(memory, google_gemini)
#     elif ai_model == 'ImageGenerator':
#         return image_genrate(last_user_message)["data"][0]["url"]
#     else:
#         # Default to ChatGPT if the provided AI model is invalid
#         chat_model = define_conv_chain(memory, chat_openai_gpt3)
    
#     # Get the last message from the user
#     last_user_message = message_list[-1]["content"]
    
#     try:
#         # Use the conversation chain to generate a response
#         response = chat(chat_model, ai_model, last_user_message)
#     except Exception as e:
#         # Handle the case where an error occurs during response generation
#         print(f"Error: {str(e)}")
#         # Fallback to another model or provide a default response
#         response = "آسف، لم أتمكن من إنشاء استجابة في الوقت الحالي. يرجى المحاولة مرة أخرى لاحقًا."
    
#     return response

# def generate_title_request(message_list):
#     try:
#         openai.api_key = os.getenv('OPENAI_API_KEY')
#         gpt3_response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo-16k",
#             messages=[
#                          {"role": "system",
#                           "content": "Summarize and make a very short meaningful title under 24 characters"},
#                      ] + message_list
#         )
#         response = gpt3_response["choices"][0]["message"]["content"].strip()

#     except Exception as e:
#         return "Problematic title with error."
#     return response

