from qdrant_client.http.models import VectorParams, Distance
from config.qdrant_client import get_qdrant_client
from fastembed import TextEmbedding
import uuid
from storage.chunking import chunk_text
from qdrant_client.http.models import Filter


class DocumentStore:
    """
    Handles document storage and retrieval using Qdrant.
    This is NOT an agent. Pure storage service.
    """

    COLLECTION_NAME = "documents"

    def __init__(self, vector_size: int):
        self.client = get_qdrant_client()
        self.vector_size = vector_size
        self._ensure_collection()
        self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def _ensure_collection(self) -> None:
        """
        Create collection if it does not exist.
        """
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    def save_document(self, text: str, metadata: dict | None = None) -> str:
        """
        Chunk text, embed chunks, and store them in Qdrant.
        Returns document ID.
        """
        doc_id = str(uuid.uuid4())
        chunks = chunk_text(text)

        embeddings = list(self.embedder.embed(chunks))

        points = []
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            points.append({
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "text": chunk,
                    **(metadata or {})
                }
            })


        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points
        )

        return doc_id

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_id: str | None = None
    ) -> str:
        query_vector = list(self.embedder.embed([query]))[0]

        search_filter = None
        if doc_id:
            search_filter = Filter(
                must=[
                    {
                        "key": "doc_id",
                        "match": {"value": doc_id}
                    }
                ]
            )

        response = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True
        )

        # 🔑 THIS IS THE IMPORTANT PART
        points = response.points

        texts = []
        for p in points:
            if p.payload and "text" in p.payload:
                texts.append(p.payload["text"])

        return "\n".join(texts)
