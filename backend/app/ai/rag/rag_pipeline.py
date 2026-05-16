import logging
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.config import settings

logger = logging.getLogger(__name__)


class RagPipeline:

    _instance = None

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small",
        )
        self.vectorstore = Chroma(
            collection_name=settings.RAG_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_DB_PATH,
        )
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.RAG_TOP_K},
        )
        logger.info(
            f"RAG pipeline loaded — collection: {settings.RAG_COLLECTION_NAME} "
            f"top_k: {settings.RAG_TOP_K}"
        )

    @classmethod
    def get_instance(cls) -> "RagPipeline":
        """Singleton — loaded once at startup, reused across requests."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def retrieve(self, query: str) -> str:
        """
        Takes rag_query from planner.
        Returns top K chunks as a single context string.
        """
        if not query or not query.strip():
            logger.warning("RAG retrieve called with empty query")
            return ""

        try:
            docs = self.retriever.invoke(query)

            if not docs:
                logger.info(f"RAG: no documents found for query: {query[:80]}")
                return ""

            # Join chunks with separator for LLM context
            chunks = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get("source", "sugarcane knowledge base")
                page = doc.metadata.get("page", "")
                header = f"[Chunk {i} — {source}{f', page {page}' if page else ''}]"
                chunks.append(f"{header}\n{doc.page_content}")

            context = "\n\n".join(chunks)
            logger.info(f"RAG retrieved {len(docs)} chunks for query: {query[:80]}")
            return context

        except Exception as e:
            logger.error(f"RAG retrieval error: {e}", exc_info=True)
            return ""