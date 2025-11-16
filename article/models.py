from django.db import models
from pgvector.django import VectorField


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Name')

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=512, unique=True, verbose_name='Title')
    text = models.TextField(verbose_name='Text')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, related_name='articles', null=True)

    def __str__(self):
        return self.title


class ArticleEmbedding(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='embedding',
        null=False,
        blank=False,
    )
    embedding = VectorField(dimensions=384) # intfloat / multilingual-e5-small
