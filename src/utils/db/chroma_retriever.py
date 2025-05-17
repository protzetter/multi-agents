"""
ChromaDB Retriever Module

This module provides a retriever implementation for ChromaDB vector database.
It allows for semantic search and retrieval of documents based on similarity to a query.
"""

from dataclasses import dataclass
from agent_squad.retrievers import Retriever
from typing import Any, List, Dict, Optional, Union
import chromadb
from chromadb.config import Settings
import asyncio
from chromadb.api.types import QueryResult
import logging

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class ChromaDBRetrieverOptions:
    """
    Configuration options for ChromaDB Retriever.
    
    Attributes:
        persist_directory (str): Directory where ChromaDB stores its data
        collection_name (str): Name of the ChromaDB collection to query
        n_results (int, optional): Maximum number of results to return. Defaults to 5.
        similarity_threshold (float, optional): Minimum similarity score (0-1) for results. Defaults to 0.7.
        client_settings (dict, optional): Additional settings for ChromaDB client
    """
    persist_directory: str
    collection_name: str
    n_results: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.7
    client_settings: Optional[Dict[str, Any]] = None


class ChromaDBRetriever(Retriever):
    """
    ChromaDB implementation of the Retriever abstract base class.
    Provides methods for retrieving and processing documents from a ChromaDB collection.
    
    This retriever performs semantic search on vector embeddings stored in ChromaDB
    and returns documents that are semantically similar to the query text.
    """
    def __init__(self, options: ChromaDBRetrieverOptions):
        """
        Initialize the ChromaDB retriever with configuration options.
        
        Args:
            options (ChromaDBRetrieverOptions): Configuration options for the retriever
        
        Raises:
            ValueError: If required options are missing or invalid
            chromadb.errors.NoIndexException: If the collection doesn't exist
        """
        super().__init__(options)
        
        self.options = options
        
        # Validate options
        if not self.options.persist_directory:
            raise ValueError("persist_directory must be provided")
        if not self.options.collection_name:
            raise ValueError("collection_name must be provided")
        if self.options.n_results <= 0:
            raise ValueError("n_results must be greater than 0")
        if not (0 <= self.options.similarity_threshold <= 1):
            raise ValueError("similarity_threshold must be between 0 and 1")
        
        # Initialize ChromaDB client with optional settings
        client_settings = self.options.client_settings or {}
        try:
            self.client = chromadb.PersistentClient(
                path=self.options.persist_directory,
                settings=Settings(**client_settings)
            )
            
            # Get the collection
            self.collection = self.client.get_collection(self.options.collection_name)
            logger.info(f"Successfully connected to ChromaDB collection: {self.options.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            raise

    def _execute_query(self, text: str) -> QueryResult:
        """
        Execute a synchronous query against the ChromaDB collection.
        
        Args:
            text (str): The query text to search for
            
        Returns:
            QueryResult: The raw results from ChromaDB query
            
        Raises:
            Exception: If the query fails
        """
        logger.debug(f"Executing ChromaDB query: {text[:50]}...")
        return self.collection.query(
            query_texts=[text],
            n_results=self.options.n_results,
            include=["documents", "metadatas", "distances"]
        )

    async def retrieve(self, text: str) -> List[Dict[str, Any]]:
        """
        Retrieve documents from ChromaDB that match the query text.
        
        Args:
            text (str): The query text to search for
            
        Returns:
            List[Dict[str, Any]]: List of documents with content, metadata, and similarity scores
                                 Returns empty list if no results or error occurs
        """
        if not text or not text.strip():
            logger.warning("Empty query text provided to retrieve()")
            return []
            
        try:
            # Run the synchronous query in the default executor to avoid blocking
            results = await asyncio.get_event_loop().run_in_executor(
                None, self._execute_query, text
            )
            
            # Check if results are empty
            if not results['documents'] or not results['documents'][0]:
                logger.info("No results found for query")
                return []

            formatted_results = []
            for i in range(len(results['documents'][0])):
                # Convert distance to similarity score (1 - distance)
                # ChromaDB distances are typically between 0-2 for cosine distance
                similarity_score = 1 - min(results['distances'][0][i], 1.0)
                
                # Only include results above the similarity threshold
                if similarity_score >= self.options.similarity_threshold:
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                        'similarity_score': round(similarity_score, 4)
                    }
                    formatted_results.append(result)
            
            logger.info(f"Retrieved {len(formatted_results)} results above threshold")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}", exc_info=True)
            return []

    async def retrieve_and_combine_results(self, text: str) -> Dict[str, Any]:
        """
        Retrieve documents and combine them into a single result.
        
        Args:
            text (str): The query text to search for
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - combined_content: All document contents joined together
                - sources: List of metadata and similarity scores for each source
                - total_sources: Number of sources retrieved
        """
        try:
            results = await self.retrieve(text)
            
            if not results:
                logger.info("No results to combine")
                return {
                    "combined_content": "",
                    "sources": [],
                    "total_sources": 0
                }
            
            # Sort results by similarity score (highest first)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Combine contents with clear separation between documents
            contents = [f"Document {i+1}:\n{doc['content']}" for i, doc in enumerate(results)]
            combined_content = "\n\n---\n\n".join(contents)
            
            # Prepare sources with more detailed information
            sources = [{
                "metadata": doc['metadata'],
                "similarity_score": doc['similarity_score'],
                "content_preview": doc['content'][:100] + "..." if len(doc['content']) > 100 else doc['content']
            } for doc in results]
            
            return {
                "combined_content": combined_content,
                "sources": sources,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error combining results: {str(e)}", exc_info=True)
            return {
                "combined_content": "",
                "sources": [],
                "total_sources": 0
            }

    async def retrieve_and_generate(self, text: str) -> Dict[str, Any]:
        """
        Retrieve documents and generate a summary.
        
        This method retrieves relevant documents and extracts a summary from them.
        It's useful for providing a quick overview of the retrieved information.
        
        Args:
            text (str): The query text to search for
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - generated_content: All document contents joined together
                - summary: First paragraph or excerpt from the most relevant document
                - sources: List of metadata and similarity scores for each source
                - total_sources: Number of sources retrieved
        """
        try:
            combined_results = await self.retrieve_and_combine_results(text)
            
            if not combined_results['combined_content']:
                logger.info("No content to generate summary from")
                return {
                    "generated_content": "",
                    "summary": "",
                    "sources": [],
                    "total_sources": 0
                }
            
            # Extract a meaningful summary
            # First try to get the first paragraph from the most relevant document
            if combined_results['sources'] and 'content_preview' in combined_results['sources'][0]:
                summary = combined_results['sources'][0]['content_preview']
            else:
                # Fall back to first paragraph of combined content
                content_parts = combined_results['combined_content'].split('\n\n')
                summary = content_parts[0] if content_parts else ""
            
            # Ensure summary isn't too long
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            return {
                "generated_content": combined_results['combined_content'],
                "summary": summary,
                "sources": combined_results['sources'],
                "total_sources": combined_results['total_sources']
            }
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}", exc_info=True)
            return {
                "generated_content": "",
                "summary": "",
                "sources": [],
                "total_sources": 0
            }
    
    async def health_check(self) -> Dict[str, Union[bool, str]]:
        """
        Check if the ChromaDB connection is healthy.
        
        Returns:
            Dict[str, Union[bool, str]]: Dictionary with health status and message
        """
        try:
            # Try to get collection info as a simple health check
            collection_info = self.collection.count()
            return {
                "healthy": True,
                "message": f"Connected to collection '{self.options.collection_name}' with {collection_info} documents"
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "healthy": False,
                "message": f"Failed to connect to ChromaDB: {str(e)}"
            }
