from langdetect import detect
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import openai
import json
import ast

def detect_language(text ):
    try:
        language = detect(text)
        return language
    except:
        return "Unknown"
    

def correct_the_grammar_mistakes(text_input):
    input_language = detect_language(text_input)

    try:
        # Define the instruction for the model as a system message
        instruction_message = {
            "role": "system",
            "content": f"""
Proofreading Suggestions for {input_language.upper()} Text:

Text: "{text_input}"

Please provide proofreading suggestions in the following categories:
- Spelling Mistakes
- Grammar Check
- Drafting
- Lexicon
- Other Corrections
{{
    "Spelling Mistakes": {{
        "old value": ["new value1", "new value2", ...]
    }},
    "Grammar Check": {{
        "old value": ["new value1", "new value2", ...]
    }},
    "Drafting": {{
        "old value": ["new value1", "new value2", ...]
    }},
    "Lexicon": {{
        "old value": ["new value1", "new value2", ...]
    }},
    "Other Corrections": {{
        "old value": ["new value1", "new value2", ...]
    }}
}}
"""
        }

        # Include the actual text to be processed as a user message
        text_message = {
            "role": "user",
            "content": text_input
        }

        # Combine the instruction and the text into the messages parameter
        gpt3_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[instruction_message, text_message]
        )

        # Extracting the response
        response = gpt3_response.choices[0].message.content.strip()

        # Parse the response as JSON
        response_json = json.loads(response)

    except Exception as e:
        print(e)
        return "An error occurred while processing the text."

    return response_json


# text = "كتب الطالبان مقالاً ممتعاً عن الأدب العربي. ذهبت المعلمة إلى المدرسة لإعطاء دروس إضافية. تعلم اللغة العربية يسهل التواصل مع الزملاء في العمل. قرأ الأطفال كتاً ممعة في امكتبة العامة."

# print( ast.literal_eval(correct_the_grammar_mistakes(text)))
