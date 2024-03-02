from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langdetect import detect

from langdetect import detect

def detect_language(text ):
    try:
        language = detect(text)
        return language
    except:
        return "Unknown"

from langdetect import detect
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def detect_language(text):
    try:
        language = detect(text)
        return language
    except:
        return "en"  # Default to English if language detection fails

def rephrase(text):
    input_language = detect_language(text)
    
    article_prompt = f"""Please rephrase the following text while preserving its original meaning and coherence. Aim for clarity and conciseness in your rewrite.
    The provided text is in {input_language.upper()} language:
    ``` 
    {text}
    """

    article_promptTemp = PromptTemplate(
        input_variables=["text_input", "input_language"],
        template="""You are a professional content creator and article writer. Please rephrase the following text while maintaining its original meaning and coherence.
        Ensure clarity and conciseness in your rewrite.\n\n{text_input}\n\nRephrased paragraph.
        Make sure the output text is in {input_language} language."""
    )

    google_gemini = ChatGoogleGenerativeAI(
        model="gemini-pro",
        temperature=0.5,
        convert_system_message_to_human=True,)

    print(article_prompt)
    print("================================")
    article_extraction_chain = LLMChain(llm=google_gemini, prompt=article_promptTemp)
    article = article_extraction_chain.run({"text_input": text, "input_language": input_language})
    return article
