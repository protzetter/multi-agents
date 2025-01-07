from chroma_retriever import ChromaDBRetriever, ChromaDBRetrieverOptions
import asyncio

# Configure options
options = ChromaDBRetrieverOptions(
        persist_directory= './chromadb',
        collection_name='ubs-research',
        n_results= 5,
        similarity_threshold= 0.6
)
    
# Example usage
async def main():
    try:

        retriever = ChromaDBRetriever(options)
        
        # Example query
        query = "what investments are you recommending in 2025"
        
        # Basic retrieval
        # results = await retriever.retrieve(query)
        # print("Basic retrieval results:", results)
        
        # Combined results
        combined = await retriever.retrieve_and_combine_results(query)
        print("Combined results:", combined['combined_content'])
        
        # Generated content
        # generated = await retriever.retrieve_and_generate(query)
        # print("Generated content:", generated)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())