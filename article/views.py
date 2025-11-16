from django.shortcuts import render
from django.views.generic import ListView

from .models import Article


class ArticleListView(ListView):
    model = Article
    template_name = "article/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

def article_detail(request, pk):
    article = Article.objects.get(pk=pk)

    context = {'article': article}
    return render(request, 'article/article_detail.html', context=context)
