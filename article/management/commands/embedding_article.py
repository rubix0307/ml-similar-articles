from itertools import batched
from django.core.management.base import BaseCommand
from django.db.models import Q
from article.models import Article
from article.vectorizer import VectorizerLocal
from article.services import ArticleEmbeddingService, EmbeddingServiceConfig


class Command(BaseCommand):
    help = 'Process Article to ArticleEmbedding'

    def add_arguments(self, parser):
        parser.add_argument('--batch_size', type=int, default=32)

    def handle(self, *args, **options):
        batch_size = options['batch_size']

        service_cfg = EmbeddingServiceConfig(embedding_dim=384, normalize=True, round_decimals=4, batch_size=batch_size)
        embedding_service = ArticleEmbeddingService(vectorizer=VectorizerLocal(), cfg=service_cfg)

        qs = Article.objects.filter(~Q(embedding__isnull=False)).order_by('id')

        total = qs.count()
        self.stdout.write(f'Process {total} articles without embedding...')

        start = 0
        while True:
            articles_batch = list(qs[:batch_size*5])
            if not articles_batch:
                break

            for batch in batched(articles_batch, batch_size):
                embedding_service.process_articles(batch)
                start += batch_size
                self.stdout.write(f'Processed {start}/{total}')

        self.stdout.write(self.style.SUCCESS('Done.'))