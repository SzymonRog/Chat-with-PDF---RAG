import time
from typing import List

from openai import OpenAI

from src.embeddings.cost_tracker import cost_tracker
from src.models.chunk import Chunk
from src.models.embedding import EmbeddedChunk


class OpenAIEmbedder:

    def __init__(self, model_name:str = "text-embedding-3-small"):
        self.model_name =model_name
        self.client = OpenAI()


    def embed_batch(
            self,
            chunks: List[Chunk],
            batch_size: int = 50
    ) -> List[EmbeddedChunk]:

        embedded_chunks = []

        for i in range(0 , len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            start_time = time.time()

            response = self.client.embeddings.create(
                model=self.model_name,
                input=[chunk.text for chunk in batch],
            )

            elapsed_time = time.time() - start_time
            num_tokens = response.usage.total_tokens
            cost = cost_tracker.track_request(model_name=self.model_name, num_tokens=num_tokens)

            print(f"Batch {i // batch_size + 1}: "
                  f"{num_tokens} tokens, ${cost:.6f}")


            for chunk, embedding_data in zip(batch, response.data):
                embedded_chunks.append(EmbeddedChunk(
                    chunk=chunk,
                    embedding=embedding_data.embedding,
                    model_name=self.model_name,
                    embedding_time=elapsed_time,
            ))

        return embedded_chunks

