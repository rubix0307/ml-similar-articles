from django.core.management.base import BaseCommand
from datasets import load_dataset
from django.db import transaction
from tqdm import tqdm
from article.models import Article, Topic


def save_articles(articles: list[Article]):
    if articles:
        Article.objects.bulk_create(articles, ignore_conflicts=True)


class Command(BaseCommand):
    help = 'Load news from dataset "zloelias/lenta-ru"'

    def handle(self, *args, **options):
        topic_cache = {topic.name: topic for topic in Topic.objects.all()}

        with transaction.atomic():

            Article.objects.all().delete()
            ds = load_dataset('zloelias/lenta-ru', split='train', streaming=True).take(100_000)

            self.stdout.write('Start...')
            article_buffer = []
            for num, article_data in enumerate(tqdm(ds), start=1):
                article_data: dict

                topic_name = article_data.get('topic')
                title = article_data.get('title')
                text = article_data.get('text')

                if not all([topic_name, title, text]):
                    continue

                topic_obj = topic_cache.get(topic_name)
                if not topic_obj:
                    topic_obj, created = Topic.objects.get_or_create(
                        name=topic_name,
                    )
                    topic_cache[topic_name] = topic_obj

                article_buffer.append(
                    Article(
                        title=title,
                        text=text,
                        topic=topic_obj,
                    )
                )
                if num % 100 == 0:
                    try:
                        save_articles(article_buffer)
                    finally:
                        article_buffer = []
            save_articles(article_buffer)

            self.stdout.write(self.style.SUCCESS('Done'))