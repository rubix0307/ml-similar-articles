from django.contrib import admin
from django.db.models import Value, Case, When, TextField
from django.db.models.functions import Concat, Substr, Length

from article.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_text_content', 'topic__name')
    list_filter = ('topic',)

    list_select_related = ('topic',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        queryset = (
            queryset
            .only('id', 'title', 'topic_id',)
            .annotate(text_len=Length('text'))
            .annotate(
                short_text_content=Case(
                    When(
                        text_len__gt=150,
                        then=Concat(Substr('text', 1, 150), Value('...'))
                    ),
                    default='text',
                    output_field=TextField(),
                )
            )
        )
        return queryset

    @admin.display(description='Short text content')
    def short_text_content(self, obj):
        return obj.short_text_content
