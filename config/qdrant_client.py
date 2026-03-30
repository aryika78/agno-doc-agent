import os
from qdrant_client import QdrantClient


def get_qdrant_client() -> QdrantClient:
    """
    Centralized Qdrant client factory.
    Keeps connection logic in one place.
    """
    return QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", "6333"))
    )
