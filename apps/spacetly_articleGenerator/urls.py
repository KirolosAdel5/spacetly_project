from django.urls import path
from . import views

app_name = 'spacetly_article_generator'
# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('article-id/', GenerateUUIDAPIView.as_view(), name='generate_uuid'),
    path('generate-keywords/', KeywordGeneratorView.as_view(), name='generate-keywords'),

    # path('<uuid:article_id>/', ArticleStepView.as_view(), name='article_step'),
    # path('<uuid:article_id>/info/', ArticleStepInfoView.as_view(), name='article_step_info'),

    path('generate_Titles/', TitleGeneratorView.as_view(), name='generated_Titles'),
    path('generate_SubTitles/', Subtitle_GeneratorView.as_view(), name='Subtitle_GeneratorView'),
    
    path('generate_Articles/<uuid:article_id>/', Article_GeneratorView.as_view(), name='Article_GeneratorView'),

    #get all articles 
    path('get_all_articles/', UserArticleListView.as_view(), name='get_all_articles'),    
    path('get_article_detail/<uuid:pk>/', UserArticleDetailView.as_view(), name='get_article_detail'),    

]
