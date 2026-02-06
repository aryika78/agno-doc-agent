from qdrant_client.http.models import VectorParams, Distance
from config.qdrant_client import get_qdrant_client


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
