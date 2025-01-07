from dataclasses import dataclass
from multi_agent_orchestrator.retrievers import Retriever
from typing import Any, List, Dict,Optional
import chromadb
from chromadb.config import Settings
import asyncio
from chromadb.api.types import QueryResult

@dataclass
class ChromaDBRetrieverOptions:
    """Options for Amazon Kb Retriever."""
    persist_directory: str
    collection_name: str
    n_results: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.7


class ChromaDBRetriever(Retriever):
    """
    ChromaDB implementation of the Retriever abstract base class.
    Provides methods for retrieving and processing documents from a ChromaDB collection.
    """
    def __init__(self, options: ChromaDBRetrieverOptions):
        """
        Initialize the ChromaDB retriever with configuration options.
        
        Args:
            options : ChromaDBRetrieverOptions
        """
        super().__init__(options)
        
        self.options = options
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.options.persist_directory
        )
        
        # Get the collection
        self.collection = self.client.get_collection(self.options.collection_name)

    def _execute_query(self, text: str) -> QueryResult:
        """Synchronous method to execute ChromaDB query"""
        return self.collection.query(
            query_texts=[text],
            n_results=self.options.n_results,
            include=["documents", "metadatas", "distances"]
        )

    async def retrieve(self, text: str) -> List[Dict[str, Any]]:
        try:
            # Run the synchronous query in the default executor
            results = await asyncio.get_event_loop().run_in_executor(
                None, self._execute_query, text
            )
            
            if not results['documents'][0]:  # Check if results are empty
                return []

            formatted_results = []
            for i in range(len(results['documents'][0])):
                # Convert distance to similarity score (1 - distance)
                similarity_score = 1 - results['distances'][0][i]
                if similarity_score >= self.options.similarity_threshold:
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': similarity_score
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during retrieval: {str(e)}")
            return []

    async def retrieve_and_combine_results(self, text: str) -> Dict[str, Any]:
        try:
            results = await self.retrieve(text)
            
            if not results:
                return {
                    "combined_content": "",
                    "sources": [],
                    "total_sources": 0
                }
            
            # Combine contents
            contents = [doc['content'] for doc in results]
            combined_content = "\n\n".join(contents)
            
            # Prepare sources
            sources = [{
                "metadata": doc['metadata'],
                "similarity_score": doc['similarity_score']
            } for doc in results]
            
            return {
                "combined_content": combined_content,
                "sources": sources,
                "total_sources": len(sources)
            }
            
        except Exception as e:
            print(f"Error combining results: {str(e)}")
            return {
                "combined_content": "",
                "sources": [],
                "total_sources": 0
            }

    async def retrieve_and_generate(self, text: str) -> Dict[str, Any]:
        try:
            combined_results = await self.retrieve_and_combine_results(text)
            
            if not combined_results['combined_content']:
                return {
                    "generated_content": "",
                    "summary": "",
                    "sources": [],
                    "total_sources": 0
                }
            
            # Extract first paragraph as summary
            content_parts = combined_results['combined_content'].split('\n\n')
            summary = content_parts[0] if content_parts else ""
            
            return {
                "generated_content": combined_results['combined_content'],
                "summary": summary,
                "sources": combined_results['sources'],
                "total_sources": combined_results['total_sources']
            }
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return {
                "generated_content": "",
                "summary": "",
                "sources": [],
                "total_sources": 0
            }
