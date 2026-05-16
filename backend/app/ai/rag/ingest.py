import logging
import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings

logger = logging.getLogger(__name__)

# Path to your sugarcane knowledge documents
DOCS_PATH = "app/ai/rag/documents"


def load_documents():
    """
    Load all PDFs and text files from documents folder.
    Add your sugarcane study book PDF here.
    """
    if not os.path.exists(DOCS_PATH):
        raise FileNotFoundError(
            f"Documents folder not found: {DOCS_PATH}\n"
            f"Create this folder and add your sugarcane PDF books."
        )

    documents = []

    # Load PDFs
    pdf_loader = DirectoryLoader(
        DOCS_PATH,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    pdf_docs = pdf_loader.load()
    documents.extend(pdf_docs)
    logger.info(f"Loaded {len(pdf_docs)} PDF pages")

    if not documents:
        raise ValueError(
            f"No documents found in {DOCS_PATH}. "
            f"Add your sugarcane study book PDF."
        )

    return documents


def chunk_documents(documents):
    """
    Split documents into chunks for embedding.
    Uses semantic chunking — splits on paragraphs first.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", " "],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks")
    return chunks


def add_metadata(chunks, crop_name: str = "sugarcane"):
    """
    Tag every chunk with crop metadata.
    Helps with filtered retrieval in future.
    """
    for chunk in chunks:
        chunk.metadata["crop"] = crop_name
        chunk.metadata["collection"] = settings.RAG_COLLECTION_NAME
    return chunks


def ingest():
    """
    Main ingestion pipeline.
    Run this once to build the Chroma vector store.
    Run again when you add new documents — it will update the store.

    Usage:
        python -m app.ai.rag.ingest
    """
    logger.info("Starting RAG ingestion pipeline...")

    # Step 1 — Load documents
    logger.info(f"Loading documents from: {DOCS_PATH}")
    documents = load_documents()
    logger.info(f"Total pages loaded: {len(documents)}")

    # Step 2 — Chunk
    chunks = chunk_documents(documents)

    # Step 3 — Add metadata
    chunks = add_metadata(chunks)

    # Step 4 — Embed and store in Chroma
    logger.info("Embedding chunks and storing in Chroma...")
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-small",
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.RAG_COLLECTION_NAME,
        persist_directory=settings.CHROMA_DB_PATH,
    )

    count = vectorstore._collection.count()
    logger.info(f"Ingestion complete — {count} chunks stored in Chroma")
    logger.info(f"Chroma DB path: {settings.CHROMA_DB_PATH}")
    print(f"✅ Ingestion complete — {count} chunks stored")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    ingest()