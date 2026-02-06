from qdrant_client import QdrantClient


def get_qdrant_client() -> QdrantClient:
    """
    Centralized Qdrant client factory.
    Keeps connection logic in one place.
    """
    return QdrantClient(
        host="localhost",
        port=6333
    )
