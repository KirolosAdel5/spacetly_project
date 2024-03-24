import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated
from .models import Articles
from .tasks import generate_And_Get_KeyWords ,generate_And_Get_Titles,generate_And_Get_Subtitles , full_article
from  .serializers import AllArticlesSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter,OrderingFilter

class LastArticlesPagination(LimitOffsetPagination):
    """
    Pagination class for last  articles.
    """
    default_limit = 10
    max_limit = 10
    
class UserArticleListView(generics.ListAPIView):
    queryset = Articles.objects.all()
    serializer_class = AllArticlesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LastArticlesPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        # Filter articles by the current user
        return self.queryset.filter(user=self.request.user)

class UserArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Articles.objects.all()
    serializer_class = AllArticlesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter articles by the current user
        
        return self.queryset.filter(user=self.request.user)
class GenerateUUIDAPIView(APIView):
    def post(self, request):
        # Generate UUID
        generated_uuid = uuid.uuid4()

        # Return the UUID in the response
        return Response({'article_id': str(generated_uuid)}, status=status.HTTP_200_OK)

class KeywordGeneratorView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # Check if 'topic' and 'language' keys exist in request.data
        if 'topic' not in request.data or 'language' not in request.data:
            return Response({"error": "You must provide both 'topic' and 'language'."}, status=400)
        
        # Extract data from request
        topic = request.data.get('topic')
        language = request.data.get('language')
        num_of_keywords = request.data.get('num_of_keywords', 10)  # Default to 10 if not provided

        # Generate keywords
        keywords = generate_And_Get_KeyWords(topic, num_of_keywords, language)

        return Response({"keywords": keywords} , status=status.HTTP_200_OK)
class TitleGeneratorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check if 'topic' and 'language' keys exist in request.data
        if 'topic' not in request.data or 'language' not in request.data:
            return Response({"error": "You must enter topic dnd language"}, status=400)
        
        topic = request.data.get('topic', '')
        num_titles = request.data.get('num_titles', 10)
        language = request.data.get('language', '')
        tone_of_voice = request.data.get('tone_of_voice', '')
        keywords = request.data.get('keywords', [])

        # Check if required fields are empty
        if topic == '' or language == '' or tone_of_voice == '':
            return Response({"error": "You must enter topic, language, and tone_of_voice."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate Titles
        generated_titles = generate_And_Get_Titles(topic, keywords, num_titles, tone_of_voice, language)
        return Response({"titles": generated_titles}, status=status.HTTP_200_OK)
    
class Subtitle_GeneratorView(APIView):
    #authentication_classes = [TokenAuthentication] 
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check if 'topic' and 'language' keys exist in request.data
        if 'title' not in request.data or 'language' not in request.data:
            return Response({"error": "You must enter topic, language, and tone_of_voice"}, status=400)
        

        title = request.data.get('title', '')
        num_Of_points= request.data.get('num_Of_points', 3)
        language=request.data.get('language', '')
        tone_of_voice= request.data.get('tone_of_voice', '')
        keywords=request.data.get('keywords', [])


        # Generate Titles
        if title == '' or language == '' or tone_of_voice =='':
            return Response({"error": "you must enter topic and language "}, status=403) 
       
        generated_SubTitles = []
        for i in range(3):
            generated_SubTitles.append(generate_And_Get_Subtitles(Title = title , Opening_Keywords = keywords,toneOfVoice  = tone_of_voice , language = language ,  num_of_points_in_Subtitle = num_Of_points ))
                # print(generated_Titles)   
        return Response({"SubTitles": generated_SubTitles })

class Article_GeneratorView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AllArticlesSerializer
    def post(self, request,article_id, *args, **kwargs):
        # Check if 'topic' and 'language' keys exist in request.data
        if 'title' not in request.data or 'language' not in request.data or 'num_Article_words' not in request.data:
            return Response({"error": "You must enter topic, language, and num_Article_words"}, status=400)
        
        article_title = request.data.get('title', '')
        subTitles =    request.data.get('selected_SubTitles', [])
        opening_keywords = request.data.get('keywords', [])
        num_Article_words = request.data.get('num_Article_words', '') # Assuming this is a typo and should be 'num_Article_words'
        language = request.data.get('language', '')
        tone_of_voice =    request.data.get('tone_of_voice', '')

        if not (article_title and language and tone_of_voice):
            return Response({"error": "You must enter a topic, language, and tone of voice."}, status=403)

        # Assuming article_generator returns the generated article content
        article_context = full_article(idea= article_title, outline_list = subTitles ,
                                        num_of_words = num_Article_words , tone_of_voice = tone_of_voice , language = language )

        try:
            # Attempt to retrieve the article by its ID
            article = Articles.objects.get(id=article_id)
            
            # Update the fields
            article.title = article_title
            article.subtitles = subTitles
            article.keywords = opening_keywords
            article.content = article_context
            article.language = language
            article.tone_of_voice = tone_of_voice
            
            # Save the updated article
            article.save()
            serializer = AllArticlesSerializer(article)

            # Return success response
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Articles.DoesNotExist:
            # If the article with the given ID doesn't exist, create a new one
            article = Articles.objects.create(
                id=article_id,
                user=request.user,
                title=article_title,
                subtitles=subTitles,
                keywords=opening_keywords,
                content=article_context,
                language=language,
                tone_of_voice=tone_of_voice
            )
            
            serializer = AllArticlesSerializer(article)

            # Return success response
            return Response(serializer.data, status=status.HTTP_201_CREATED)

# class ArticleStepView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, article_id):
#         step = request.query_params.get('step')
        
    
       
#         # Check if step parameter is provided and handle the logic accordingly
#         if step == '0':
#             # Try to retrieve the article with the provided ID
#             article = Articles.objects.filter(id=article_id, user=request.user).first()
#             if article:
#                 # Update step 0 data if provided in request
#                 data = request.data
#                 if 'topic' in data:
#                     article.step0['topic'] = data['topic']
#                 if 'language' in data:
#                     article.step0['language'] = data['language']
#                 if 'selected_keywords' in data:
#                     article.step0['selected_keywords'] = data['selected_keywords']
#                 if 'num_keywords' in data:
#                     article.step0['num_keywords'] = data['num_keywords']
#                 # Save the modified article instance
#                 article.save()
                  
#                 # Return the updated step 0 data
#                 return Response(article.step0, status=status.HTTP_200_OK)
#             else:
#                 # Ensure required fields are provided
#                 required_fields = ['topic', 'language', 'selected_keywords']
#                 if not all(field in request.data for field in required_fields):
#                     return Response({"error": "Missing required fields: topic, language, selected_keywords"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # Extract data from request with default values
#                 topic = request.data.get('topic', '')
#                 language = request.data.get('language', '')
#                 num_keywords = request.data.get('num_keywords', 10)
#                 selected_keywords = request.data.get('selected_keywords', [])
                
#                 # Create the article with the extracted data
#                 article = Articles.objects.create(
#                     id=article_id,
#                     user=request.user,
#                     step0={
#                         'topic': topic,
#                         'language': language,
#                         'num_keywords': num_keywords,
#                         'selected_keywords': selected_keywords,
#                     }
#                 )
#                 article.save()
#                 # Return the created article's step 0 data
#                 return Response(article.step0, status=status.HTTP_201_CREATED)

#         elif step == '1':
#             # Try to retrieve the article with the provided ID
#             article = Articles.objects.filter(id=article_id).first()
#             if article:
#                 # Update step 0 data if provided in request
#                 data = request.data
#                 if 'topic' in data:
#                     article.step1['topic'] = data['topic']
#                 if 'language' in data:
#                     article.step1['language'] = data['language']
#                 if 'keywords' in data:
#                     article.step1['keywords'] = data['keywords']
#                 if 'num_titles' in data:
#                     article.step1['num_titles'] = data['num_titles']
#                 if 'tone_of_voice' in data:
#                     article.step1['tone_of_voice'] = data['tone_of_voice']
#                 # Save the modified article instance
#                 if 'selected_title' in data:
#                     article.step1['selected_title'] = data['selected_title']
#                 article.save()
                
#                 # Return the updated step 1 data
#                 return Response(article.step1, status=status.HTTP_200_OK)


#             else:
#                 # Ensure required fields are provided
#                 required_fields = ['topic', 'language', 'keywords']
#                 if not all(field in request.data for field in required_fields):
#                     return Response({"error": "Missing required fields: topic, language, keywords"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # Extract data from request with default values
#                 topic = request.data.get('topic', '')
#                 selected_title = request.data.get('selected_title', '')
#                 language = request.data.get('language', '')
#                 num_titles = request.data.get('num_titles', 3)
#                 tone_of_voice = request.data.get('tone_of_voice', 'professional')
#                 keywords = request.data.get('keywords', [])
                
#                 if selected_title == '':
#                     return Response({"error": "Missing required field: selected_title"}, status=status.HTTP_400_BAD_REQUEST)
#                 # Create the article with the extracted data
                
#                 article = Articles.objects.create(
#                     id=article_id,
#                     user=request.user,
#                     step1={
#                         'topic': topic,
#                         'selected_title': selected_title,
#                         'language': language,
#                         'keywords': keywords,
#                         'num_titles': num_titles,
#                         'tone_of_voice': tone_of_voice,
#                     }
#                 )
#                 article.save()
#                 # Return the created article's step 0 data
#                 return Response(article.step1, status=status.HTTP_201_CREATED)

#         elif step == '2':
#             # Try to retrieve the article with the provided ID
#             article = Articles.objects.filter(id=article_id).first()
            
#             if article:
#                 # Update step 0 data if provided in request
#                 data = request.data
#                 if 'title' in data:
#                     article.step2['title'] = data['title']
#                 if 'language' in data:
#                     article.step2['language'] = data['language']
#                 if 'keywords' in data:
#                     article.step2['keywords'] = data['keywords']
#                 if 'num_Of_points' in data:
#                     article.step2['num_Of_points'] = data['num_Of_points']
#                 if 'tone_of_voice' in data:
#                     article.step2['tone_of_voice'] = data['tone_of_voice']
#                 # Save the modified article instance
#                 if 'selected_SubTitles' in data:
#                     article.step2['selected_SubTitles'] = data['selected_SubTitles']
#                 article.save()
                
#                 # Return the updated step 1 data
#                 return Response(article.step2, status=status.HTTP_200_OK)
   
#             else:
#                 # Ensure required fields are provided
#                 required_fields = ['title', 'language', 'keywords']
#                 if not all(field in request.data for field in required_fields):
#                     return Response({"error": "Missing required fields: title, language, keywords"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # Extract data from request with default values
#                 title = request.data.get('title', '')
#                 selected_SubTitles = request.data.get('selected_SubTitles', [])
#                 language = request.data.get('language', '')
#                 num_Of_points = request.data.get('num_Of_points', 3)
#                 tone_of_voice = request.data.get('tone_of_voice', 'professional')
#                 keywords = request.data.get('keywords', [])
                
#                 if selected_SubTitles == '':
#                     return Response({"error": "Missing required field: selected_SubTitles"}, status=status.HTTP_400_BAD_REQUEST)
#                 # Create the article with the extracted data
                
#                 article = Articles.objects.create(
#                     id=article_id,
#                     user=request.user,
#                     step2={
#                         'title': title,
#                         'selected_SubTitles': selected_SubTitles,
#                         'language': language,
#                         'keywords': keywords,
#                         'num_Of_points': num_Of_points,
#                         'tone_of_voice': tone_of_voice,
#                     }
#                 )
#                 article.save()
#                 # Return the created article's step 2 data
#                 return Response(article.step2, status=status.HTTP_201_CREATED)

#         elif step == '3':
#             # Try to retrieve the article with the provided ID
#             article = Articles.objects.filter(id=article_id, user=request.user).first()
#             if article:
#                 # Update step 3 data if provided in request
#                 data = request.data
#                 if 'title' in data:
#                     article.step3['title'] = data['title']
#                 if 'language' in data:
#                     article.step3['language'] = data['language']
#                 if 'keywords' in data:
#                     article.step3['keywords'] = data['keywords']
#                 if 'num_Article_words' in data:
#                     article.step3['num_Article_words'] = data['num_Article_words']
#                 if 'tone_of_voice' in data:
#                     article.step3['tone_of_voice'] = data['tone_of_voice']
#                 # Save the modified article instance
#                 if 'selected_SubTitles' in data:
#                     article.step3['selected_SubTitles'] = data['selected_SubTitles']
#                 return Response(article.step3, status=status.HTTP_200_OK)            

#             else:
#                 # Ensure required fields are provided
#                 required_fields = ['title', 'language', 'keywords','num_Article_words']
#                 if not all(field in request.data for field in required_fields):
#                     return Response({"error": "Missing required fields: title, language, keywords,num_Article_words"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # Extract data from request with default values
#                 title = request.data.get('title', '')
#                 selected_SubTitles = request.data.get('selected_SubTitles', [])
#                 language = request.data.get('language', '')
#                 num_Article_words = request.data.get('num_Article_words', 300)
#                 tone_of_voice = request.data.get('tone_of_voice', 'professional')
#                 keywords = request.data.get('keywords', [])
                
#                 if num_Article_words == '':
#                     return Response({"error": "Missing required field: num_Article_words"}, status=status.HTTP_400_BAD_REQUEST)
#                 # Create the article with the extracted data
                
#                 article = Articles.objects.create(
#                     id=article_id,
#                     user=request.user,
#                     step3={
#                         'title': title,
#                         'selected_SubTitles': selected_SubTitles,
#                         'language': language,
#                         'keywords': keywords,
#                         'num_Article_words': num_Article_words,
#                         'tone_of_voice': tone_of_voice,
#                     }
#                 )
#                 article.save()
#                 # Return the created article's step 3 data
#                 return Response(article.step3, status=status.HTTP_201_CREATED)
            
#         else:
#             return Response({"error": "Invalid step number"}, status=status.HTTP_400_BAD_REQUEST)

# class ArticleStepInfoView(APIView):
#     def get(self, request, article_id):
#         # Extract the step number from the query parameters
#         step = request.query_params.get('step')
        
#         # Check if the step parameter is provided and if it's equal to '0'
#         if step == '0':
#             try:
#                 # Retrieve the article with the given ID
#                 article = Articles.objects.get(id=article_id)
                
#                 # Retrieve the step0 data from the article
#                 step0_data = article.step0
                
#                 # Return the step0 data in the response
#                 return Response(step0_data, status=status.HTTP_200_OK)
#             except Articles.DoesNotExist:
#                 # If the article with the given ID does not exist, return a 404 Not Found response
#                 return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         elif step == '1':
#             try:
#                 # Retrieve the article with the given ID
#                 article = Articles.objects.get(id=article_id)
                
#                 # Retrieve the step0 data from the article
#                 step1_data = article.step1
                
#                 # Return the step0 data in the response
#                 return Response(step1_data, status=status.HTTP_200_OK)
#             except Articles.DoesNotExist:
#                 # If the article with the given ID does not exist, return a 404 Not Found response
#                 return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         elif step == '2':
#             try:
#                 # Retrieve the article with the given ID
#                 article = Articles.objects.get(id=article_id)
                
#                 # Retrieve the step0 data from the article
#                 step2_data = article.step2
                
#                 # Return the step0 data in the response
#                 return Response(step2_data, status=status.HTTP_200_OK)
#             except Articles.DoesNotExist:
#                 # If the article with the given ID does not exist, return a 404 Not Found response
#                 return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)
          
                
#         elif step == '3':
#             try:
#                 # Retrieve the article with the given ID
#                 article = Articles.objects.get(id=article_id)
                
#                 # Retrieve the step0 data from the article
#                 step3_data = article.step3
                
#                 # Return the step0 data in the response
#                 return Response(step3_data, status=status.HTTP_200_OK)
#             except Articles.DoesNotExist:
#                 # If the article with the given ID does not exist, return a 404 Not Found response
#                 return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)
           
#         else:
#             # If the step parameter is not provided or it's not equal to '1', return a 400 Bad Request response
#             return Response({"error": "Invalid step number"}, status=status.HTTP_400_BAD_REQUEST)
