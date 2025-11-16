import django.db.models.deletion
import pgvector.django.vector
from pgvector.django import VectorExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0001_initial'),
    ]

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name='ArticleEmbedding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', pgvector.django.vector.VectorField(dimensions=384)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='embedding', to='article.article')),
            ],
        ),
    ]
