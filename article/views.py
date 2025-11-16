from django.core.exceptions import ValidationError
from django.db import connection
from django.shortcuts import render
from django.views.generic import ListView
from .models import Article


class ArticleListView(ListView):
    model = Article
    template_name = 'article/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10



def get_similar_articles(article_id: int, limit: int = 10):
    if limit < 1:
        raise ValidationError('Limit must be greater than 0')

    raw_sql = f"""
         WITH target_chunks AS (
            SELECT embedding
            FROM article_articleembedding
            WHERE article_id = {article_id}
        ),
        similarities AS (
            SELECT 
                a.article_id,
                1 - (a.embedding <=> t.embedding) AS similarity
            FROM target_chunks t
            CROSS JOIN LATERAL (
                SELECT a.article_id, a.embedding
                FROM article_articleembedding a
                -- WHERE a.article_id != {article_id} -- deactivated only for showing true result
                ORDER BY a.embedding <=> t.embedding ASC
                LIMIT 500
            ) a
        ),
        aggregated AS (
            SELECT 
                article_id,
                ROUND(SUM(similarity)::numeric, 6) AS total_score,
                COUNT(*) AS matches
            FROM similarities
            GROUP BY article_id
        )
        SELECT 
            article_id,
            ROUND(total_score / matches, 3) as total_score,
            matches
        FROM aggregated
        ORDER BY total_score DESC
        LIMIT {limit};
    """

    with connection.cursor() as cursor:
        cursor.execute(raw_sql)
        rows = cursor.fetchall()

    ids = [row[0] for row in rows]
    similarity_scores = [row[1] for row in rows]
    a_dict = {a.id: a for a in Article.objects.filter(pk__in=ids)}

    articles = []
    for a_id, score in zip(ids, similarity_scores):
        article = a_dict[a_id]
        article.similarity_score = score
        articles.append(article)

    return [a_dict.get(a_id) for a_id in ids]


def article_detail(request, pk):
    article = Article.objects.get(pk=pk)

    context = {
        'article': article,
        'similar_articles': get_similar_articles(article_id=article.id, limit=50),
    }
    return render(request, 'article/article_detail.html', context=context)
