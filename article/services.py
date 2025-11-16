from __future__ import annotations
import math
import logging
from typing import Iterable, Optional
from django.db import transaction
from .interfaces import Vectorizer, EmbeddingServiceConfig
from .models import Article, ArticleEmbedding


logger = logging.getLogger(__name__)

class ArticleEmbeddingService:

    def __init__(self, vectorizer: Vectorizer, cfg: Optional[EmbeddingServiceConfig]=None):
        self.vectorizer = vectorizer
        self.cfg = cfg or EmbeddingServiceConfig()

    def _validate_and_fix_vector(self, v: list[float]) -> list[float]:
        """
        :exception TypeError
        :exception ValueError
        """

        if not isinstance(v, list):
            raise TypeError('Vector must be a list of floats')

        if len(v) != self.cfg.embedding_dim:
            raise ValueError('Vector length (%d) != expected (%d).', len(v), self.cfg.embedding_dim)

        if self.cfg.normalize:
            v = self._l2_normalize(v)

        if self.cfg.round_decimals is not None:
            v = [round(x, self.cfg.round_decimals) for x in v]

        return v

    @staticmethod
    def _l2_normalize(v: list[float]) -> list[float]:
        norm = math.sqrt(sum(x * x for x in v))
        if norm == 0:
            return v
        return [x / norm for x in v]

    def process_article(self, article: Article) -> list[ArticleEmbedding]:
        """
        :exception ValueError
        """

        text = article.text or article.title
        if not text:
            raise ValueError('Article has no text/title to embed')

        embeddings = self.vectorizer.embed_article(article=article, batch_size=32)

        db_objects = []
        with transaction.atomic():
            ArticleEmbedding.objects.filter(article=article).delete()
            db_objects.extend(
                ArticleEmbedding.objects.bulk_create(
                    [ArticleEmbedding(article_id=e_data.article_id, embedding=self._validate_and_fix_vector(e_data.embedding))
                     for e_data in embeddings
                     ]
                )
            )
        return db_objects

    def process_articles(self, articles: Iterable[Article]) -> list[ArticleEmbedding]:
        """
        :exception RuntimeError
        """

        articles_list = list(articles)
        if not articles_list:
            return []

        db_objects = []
        for article in articles_list:
            db_objects.extend(
                self.process_article(article=article)
            )
        return db_objects