from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

google_gemini = ChatGoogleGenerativeAI(
        model="gemini-pro",
        temperature=0.5,
        convert_system_message_to_human=True,
    )


def get_prompt(target_service ,  tone_of_voice , topic ,language ,target_audience):
    d = {
        
        'Suggest_company_name': [f"""Given the following details about a new company, suggest a creative and relevant name that reflects its industry, values, 
                                and unique selling points. The company operates in the {topic} industry, 
                                It targets {target_audience}, Tone should be {tone_of_voice}. """
                                
                                ,"You are a skilled branding expert and creative thinker."],
        #___________________
        
        'new_product_ideas': [f"Generate innovative product ideas for the topic of '{topic}' tailored to {target_audience}. The ideas should be presented with a {tone_of_voice} tone, ensuring they resonate well with the intended audience. Consider the current demands and trends relevant to the topic, and how the product can address these in a unique and impactful way  The ideas are to be presented in {language.upper()} language."
                              
                              ,""" You are a talented product designer with a deep understanding of market trends and consumer needs. Your task is to conceptualize innovative products based on the following input:
                                {text_input}
                                Your concepts should be visionary yet achievable, potentially disrupting the market and offering genuine value to the target audience. Despite the broad prompt, focus on creating detailed, specific product ideas that align with the given input.
                                Provide a list of product ideas with a brief description for each, ensuring they're presented in a manner that's engaging and understandable to the target audience."""],
         #___________________
         
        'Product_description': [f"""Consider the topic '{topic}' and generate innovative product ideas that cater to {target_audience}. The presentation of these ideas should adopt a {tone_of_voice} tone. This exercise is aimed at creating concepts that are not only relevant and appealing to the specified audience but also reflective of current trends and demands within the given topic area.
                                    The instructions and ideas should be conveyed in {language.upper()} language."""
                            
                                , """ You are a talented product designer with a deep understanding of market trends and consumer needs. Your task is to conceptualize innovative products based on the following input:
                                    {text_input}
                                    Your concepts should be visionary yet achievable, potentially disrupting the market and offering genuine value to the target audience. Despite the broad prompt, focus on creating detailed, specific product ideas that align with the given input.
                                    Provide a list of product ideas with a brief description for each, ensuring they're presented in a manner that's engaging and understandable to the target audience."""],
        
         #___________________
         
        'Product_Features':    [f"""Develop a detailed list of features for a product within the '{topic}' category, ensuring the description resonates with {target_audience}. The features should be articulated in a {tone_of_voice} tone, effectively communicating the product's advantages and how it meets the needs or interests of the target demographic.
                                The detailed features should be presented in {language.upper()} language.
                                """
                                
                                ,"""You are an experienced product manager with a deep understanding of market demands and consumer preferences. Your task is to expand on the following basic product overview, detailing its features in a way that highlights the product's uniqueness and value proposition:
                                    {text_input}
                                    Focus on creating a comprehensive list of features that are directly aligned with the needs and expectations of the target audience. Your description should also reflect the specified tone of voice, making the product stand out in a competitive market.
                                    List the product features with detailed explanations, ensuring they are communicated effectively for promotional materials or product specifications."""],
         #___________________

        'suugest_product_name': [f"""Create innovative and marketable product names for a new offering in the '{topic}' category, tailored specifically to {target_audience}. The names should reflect a {tone_of_voice} tone, ensuring they capture the essence of the product while appealing directly to the intended demographic.
                                    The product names should be suitable for presentation in {language.upper()} language.
                                    """
                                    
                                ,"""As a creative marketer with expertise in branding and naming conventions, your task is to generate compelling names for the following product concept:
                                    {text_input}
                                    Your suggestions should be unique, memorable, and convey the product's value and appeal to the target audience. They should also resonate with the specified tone of voice, enhancing brand identity and market positioning.
                                    Provide a list of suggested product names, each accompanied by a brief rationale explaining how it aligns with the product concept and appeals to the intended demographic."""],
         #___________________

        'companys_mission':      [f"""Develop a compelling and succinct mission statement for a company operating within the '{topic}' domain, designed to resonate with {target_audience}. The mission statement should encapsulate the company's core purpose, values, and vision, all expressed in a {tone_of_voice} tone. It should articulate the company's commitment to its customers, stakeholders, and the broader community.
                                      The mission statement should be crafted in {language.upper()} language."""
                                 
                                , """As a strategic communications expert with a flair for brand identity, your task is to formulate a mission statement based on the following key points:
                                    {text_input}
                                    This mission statement should clearly communicate the company's ethos, objectives, and the value it aims to deliver to its target audience. Ensure that it reflects the specified tone of voice, effectively conveying the company's unique stance and commitment to excellence.
                                    Craft the mission statement, ensuring it is inspiring, concise, and aligns with the company's strategic goals and audience expectations."""], 
         #___________________

        'Slojan':                [f"""Develop captivating and intelligent slogans for a brand operating within the '{topic}' domain, which should engage {target_audience}. The slogans need to embody the brand's identity and values, all while being presented in a {tone_of_voice} tone. These should be memorable, succinct, and powerful enough to resonate with the intended demographic, emphasizing the brand's unique position in the market.
                                    The slogans should be crafted in {language.upper()} language."""
                                    
                                ,""" As a branding expert with a talent for creating memorable and impactful messaging, your task is to generate slogans based on the following brand overview:
                                    {text_input}
                                    These slogans should succinctly capture the essence of the brand, appealing directly to target_audience and reflecting the specified tone_of_voice. They should be innovative, setting the brand apart in the competitive landscape of the Slojan industry.
                                    List several slogan options, each accompanied by a short explanation of how it conveys the brand's message and values, ensuring they are linguistically and culturally appropriate for the language speaking audience."""],
        #___________________
        
        'Company_Vision':              [f"""Formulate a visionary statement for a company involved in '{topic}', which should inspire {target_audience}. This vision statement should reflect a clear and ambitious future perspective, guided by current trends and long-term goals. It should be articulated in a {tone_of_voice} tone, encapsulating the company's aspirations and how it intends to evolve and impact its sector.
                                    The vision statement should be developed in {language.upper()} language. """
                                
                                ,"""As a strategic planner and visionary thinker, your task is to craft a vision statement from the following foundational insights:

                                    {text_input}

                                    This vision should project a forward-looking perspective, showcasing how the company aims to lead and innovate within the Company_Vision field. It must resonate with target_audience and be conveyed in a tone_of_voice manner, reflecting both ambition and practicality. The statement should guide the company's direction for the future, aligning with the identified trends and setting a framework for achieving its long-term objectives.

                                    Compose a compelling vision statement that will guide the company's strategic decisions and inspire both internal stakeholders and the broader community. """],
                                            
        #___________________
        
        'interview_Questions':  [f"""Craft a set of insightful interview questions for a feature on '{topic}', intended to captivate {target_audience}. The questions should be formulated in a {tone_of_voice} tone, designed to elicit deep, thoughtful responses that will engage readers or viewers. These questions should explore the nuances of the topic, providing fresh perspectives and insights.
                                    The interview questions should be articulated in {language.upper()} language. """
                                
                                ,""" As a journalist or content creator with expertise in interview_Questions, you are tasked with developing a series of questions based on the following context:
                                        {text_input}
                                                These questions should not only probe deeply into the subject but also resonate with target_audience, reflecting a tone_of_voice approach. They should be open-ended, encouraging detailed and engaging answers that will illuminate the topic in new and interesting ways.
                                                List your interview questions, ensuring they are structured to provide valuable insights and foster a meaningful conversation about the interview_Questions."""],
        
        #___________________
        
        'job_description':      [f"""Develop a comprehensive job description for a position related to '{topic}', which should appeal to {target_audience}. The description should be written in a {tone_of_voice} tone, clearly outlining the role's responsibilities, requirements, and benefits. It should engage potential candidates, conveying why this opportunity is unique and how it aligns with their career aspirations.
                                    The job description should be articulated in {language.upper()} language. """
                                
                                ,""" As a human resources professional with a keen understanding of job_description and the needs of target_audience, you are tasked with elaborating on the following role overview:
                                        {text_input}
                                        Transform this overview into a detailed job description, emphasizing the role's key responsibilities, desired qualifications, and the benefits of joining your organization. Reflect a tone_of_voice tone throughout the description, making it resonate with the ideal candidates and highlighting the company's culture and values.
                                        Ensure the job description is complete, compelling, and provides all necessary information for applicants to understand the role and how it fits within the broader mission and goals of the company."""],
        
        #___________________
        
        'Startup_Ideas':        [f"""Generate creative and viable startup ideas within the '{topic}' field that cater to {target_audience}. The concepts should be presented in a {tone_of_voice} tone, showcasing how they address current gaps in the market or introduce novel solutions. The ideas should resonate with the intended demographic, emphasizing potential for impact, growth, and sustainability.
                                    The startup ideas should be articulated in {language.upper()} language. """
                                
                                ,""" As an entrepreneurial strategist with insights into Startup_Ideas and an understanding of target_audience, you are tasked with developing startup ideas from the following considerations:
                                    {text_input}
                                    Your ideas should not only be innovative and fill a market need but also be feasible for implementation and growth. Reflect a tone_of_voice approach in your presentation, ensuring the concepts are compelling and clearly communicate their value proposition and differentiation in the market.
                                    List your startup ideas, providing a brief overview for each that includes the problem it solves, the target market, and the unique approach or solution it offers."""],
        
        #___________________
        
        'description_of_the_real_estate':  [f"Compose a detailed and attractive description for a real estate property within the '{topic}' category, aimed at engaging {target_audience}. Utilize a {tone_of_voice} tone to emphasize the property's key features, benefits, and its potential to satisfy the needs and aspirations of the target demographic. The goal is to produce a narrative that vividly presents the property, making it appealing and prompting potential interest and inquiries.The real estate description should be crafted in {language.upper()} language."
                            
                                ,"""As a skilled copywriter with expertise in the real estate market, particularly in the area of description_of_the_real_estate , your task is to develop a comprehensive description from the following basic details:
                                    {text_input}
                                    Your description should not only highlight the property's physical attributes and amenities but also its ambiance, location advantages, and how it aligns with the lifestyle . 
                                    Employ a tone_of_voice tone to ensure the narrative is both compelling and reflective of the property's unique selling points.
                                    Produce a refined and engaging property description that effectively markets the property to potential buyers or tenants, clearly conveying its value proposition and appeal. """],
        
        
    }
    return d[target_service]
