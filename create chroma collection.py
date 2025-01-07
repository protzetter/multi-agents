#initialize chroma vector DB variables
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from typing import Tuple, Optional, Collection
import logging
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_split_document(collection:Collection, file_path, chunk_size=1000, chunk_overlap=200):
    """
    Load a document, split it into chunks, and store in ChromaDB
    
    Args:
        file_path (str): Path to your document
        chunk_size (int): Size of text chunks
        chunk_overlap (int): Overlap between chunks
    """
    
    # Load the document

    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
   
    # Prepare documents for ChromaDB
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        documents.append(chunk.page_content)
        metadatas.append(chunk.metadata)
        ids.append(f"doc_{i}")
    
    # 6. Add documents to collection
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    
    return len(chunks)


def get_or_create_collection(
    client: chromadb.Client,
    collection_name: str,
    metadata: Optional[dict] = None
) -> Tuple[Collection, bool]:
    """
    Get existing collection or create a new one if it doesn't exist
    
    Args:
        client: ChromaDB client instance
        collection_name: Name of the collection
        metadata: Optional metadata for the collection
        
    Returns:
        Tuple[Collection, bool]: (collection, created) where created is True if new collection
    """
    try:
        # Try to get existing collection
        collection = client.get_collection(name=collection_name)
        logger.info(f"Retrieved existing collection: {collection_name}")
        return collection, False
    except Exception as e:
        logger.info(f"Collection {collection_name} not found, creating new one")
        # Create new collection if it doesn't exist
        collection = client.create_collection(
            name=collection_name,
            metadata=metadata or {"hnsw:space": "cosine"}
        )
        return collection, True
    
def main():
    [collection, created]= get_or_create_collection(client=chromadb.PersistentClient(path='./chromadb'), collection_name="ubs-research")
    if created:
        print("Collection created successfully.")
        file_path = "/Users/patrickrotzetter/Library/CloudStorage/OneDrive-Personal/Documents/dev/multi-agents/documents/Daily US_en_1628275.pdf"  # Update with your file path
        num_chunks = load_and_split_document(collection, file_path)
        print(f"Document split into {num_chunks} chunks and loaded into ChromaDB")
    else:
        print("Collection loaded successfully.")
if __name__ == "__main__":
    main()