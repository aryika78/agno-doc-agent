from qdrant_client.http.models import VectorParams, Distance, Filter
from config.qdrant_client import get_qdrant_client
from fastembed import TextEmbedding
from storage.chunking import chunk_text
import uuid


class DocumentStore:
    """
    Handles document storage and retrieval using Qdrant.
    Pure storage service.
    """

    COLLECTION_NAME = "documents"

    def __init__(self, vector_size: int):
        self.client = get_qdrant_client()
        self.vector_size = vector_size
        self._ensure_collection()
        self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]

        if self.COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

            # ✅ Create payload index AFTER collection exists
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="filename",
                field_schema="keyword"
            )

            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="doc_id",
                field_schema="keyword"
            )



    # ---------------- NEW ----------------
    def list_documents(self) -> dict:
        """
        Returns { filename: doc_id } for all indexed documents.
        """
        docs = {}

        offset = None
        while True:
            res = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                with_payload=True,
                limit=100,
                offset=offset
            )

            points, offset = res
            for p in points:
                payload = p.payload or {}
                filename = payload.get("filename")
                doc_id = payload.get("doc_id")

                if filename and doc_id:
                    docs[filename] = doc_id

            if offset is None:
                break

        return docs

    def document_exists(self, filename: str) -> str | None:
        """
        Returns doc_id if a document with this filename exists in Qdrant.
        Deterministic and safe against chunk duplication.
        """
        doc_ids = set()
        offset = None

        while True:
            points, offset = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                with_payload=True,
                limit=100,
                offset=offset,
                scroll_filter=Filter(
                    must=[
                        {"key": "filename", "match": {"value": filename}}
                    ]
                )
            )

            for p in points:
                payload = p.payload or {}
                doc_id = payload.get("doc_id")
                if doc_id:
                    doc_ids.add(doc_id)

            if offset is None:
                break

        if not doc_ids:
            return None

        # There should be exactly ONE doc_id per filename
        return next(iter(doc_ids))
    # ---------------- EXISTING ----------------
    def save_document(self, text: str, metadata: dict | None = None) -> str:
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

    def search(self, query: str, top_k: int = 5, doc_id: str | None = None) -> str:
        query_vector = list(self.embedder.embed([query]))[0]

        search_filter = None
        if doc_id:
            search_filter = Filter(
                must=[{"key": "doc_id", "match": {"value": doc_id}}]
            )

        response = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True
        )

        texts = []
        for p in response.points:
            if p.payload and "text" in p.payload:
                texts.append(p.payload["text"])

        return "\n".join(texts)
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete all vectors belonging to a document.
        """
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    {"key": "doc_id", "match": {"value": doc_id}}
                ]
            )
        )

    def reset_all_documents(self) -> None:
        """
        Dev / Debug only.
        Drops and recreates the entire collection.
        """
        self.client.delete_collection(self.COLLECTION_NAME)
        self._ensure_collection()


