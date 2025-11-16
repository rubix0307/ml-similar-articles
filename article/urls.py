from django.urls import path
from .views import ArticleListView, article_detail


urlpatterns = [
    path('', ArticleListView.as_view(), name='article_list'),
    path('/<int:pk>', article_detail, name='article_detail'),
]
