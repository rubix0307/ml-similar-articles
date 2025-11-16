from django.db import models


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