from transformers import AutoTokenizer, AutoModel
import torch
from typing import Optional, Iterable

from article.interfaces import EmbeddingResult
from article.models import Article


class VectorizerLocal:
    def __init__(
        self,
        model_name: str = 'intfloat/multilingual-e5-small',
        device: str = None,
        max_tokens: int = 500,
        overlap: int = 100,
        normalize: bool = True
    ):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.normalize = normalize

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def chunk_text(self, text: str) -> list[str]:
        if not text.strip():
            return []

        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        if len(tokens) <= self.max_tokens:
            return [text]

        chunks = []
        step = self.max_tokens - self.overlap
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i:i + self.max_tokens]
            chunks.append(
                self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            )
        return chunks

    def embed(
        self,
        text: str,
        normalize: Optional[bool] = None
    ) -> list[float]:
        if not text.strip():
            return []

        normalize = normalize if normalize is not None else self.normalize

        with torch.no_grad():
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)

            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze()

            if normalize:
                embedding = torch.nn.functional.normalize(embedding, p=2, dim=0)

            return embedding.cpu().float().tolist()

    def embed_many(
        self,
        texts: list[str],
        batch_size: int = 32,
        normalize: Optional[bool] = None
    ) -> list[list[float]]:
        if not texts:
            return []

        normalize = normalize if normalize is not None else self.normalize
        all_embeddings = []

        with torch.inference_mode(), torch.amp.autocast('cuda', dtype=torch.float16):
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                inputs = self.tokenizer(
                    batch,
                    return_tensors='pt',
                    truncation=True,
                    padding='longest',
                    max_length=512,
                ).to(self.device)

                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)

                if normalize:
                    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

                all_embeddings.extend(embeddings.cpu().float().tolist())

        return all_embeddings

    def embed_article(
        self,
        article: Article,
        batch_size: int = 32
    ) -> list[EmbeddingResult]:
        if not all([article.id, article.text]):
            return []

        chunks = self.chunk_text(article.text)
        if not chunks:
            return []

        embeddings = self.embed_many(chunks, batch_size=batch_size)

        results = []
        for chunk_idx, emb in enumerate(embeddings):
            results.append(EmbeddingResult(
                embedding=emb,
                article_id=article.id,
                chunk_id=chunk_idx,
            ))
        return results

    def embed_articles(
        self,
        articles: Iterable[Article],
        batch_size: int = 32
    ) -> list[EmbeddingResult]:
        all_results = []
        for article in articles:
            results = self.embed_article(
                article=article,
                batch_size=batch_size
            )
            all_results.extend(results)
        return all_results