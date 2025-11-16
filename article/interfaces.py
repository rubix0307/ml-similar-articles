from dataclasses import dataclass
from typing import Optional, Protocol, Iterable

from article.models import Article


@dataclass
class EmbeddingServiceConfig:
    embedding_dim: int = 384
    round_decimals: Optional[int] = None
    normalize: bool = False
    batch_size: int = 256

@dataclass
class EmbeddingResult:
    embedding: list[float]
    article_id: int
    chunk_id: Optional[int] = None

class Vectorizer(Protocol):

    def embed_article(self, article: Article, batch_size: int) -> list[EmbeddingResult]:
        ...

    def embed_articles(self,articles: Iterable[Article], batch_size: int) -> list[EmbeddingResult]:
        ...


