from chroma_retriever import ChromaDBRetriever, ChromaDBRetrieverOptions
from chromadb.api.types import QueryResult
from multi_agent_orchestrator.retrievers import Retriever
from multi_agents.chroma_retriever import ChromaDBRetriever, ChromaDBRetrieverOptions
from typing import Any, Dict, List
from typing import Dict, Any
from typing import List, Dict, Any
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import MagicMock, patch
from unittest.mock import Mock, patch
from unittest.mock import patch, MagicMock
import asyncio
import pytest
import unittest

class TestChromaRetriever(unittest.TestCase):

    def test___init___initializes_correctly(self):
        """
        Test that the ChromaDBRetriever.__init__ method correctly initializes the object
        with the given options, sets up the ChromaDB client, and retrieves the collection.
        """
        # Arrange
        mock_options = ChromaDBRetrieverOptions(
            persist_directory="/tmp/chromadb",
            collection_name="test_collection"
        )

        with patch('chromadb.PersistentClient') as mock_client:
            mock_collection = MagicMock()
            mock_client.return_value.get_collection.return_value = mock_collection

            # Act
            retriever = ChromaDBRetriever(mock_options)

            # Assert
            self.assertEqual(retriever.options, mock_options)
            mock_client.assert_called_once_with(path="/tmp/chromadb")
            mock_client.return_value.get_collection.assert_called_once_with("test_collection")
            self.assertEqual(retriever.collection, mock_collection)

    def test__execute_query_1(self):
        """
        Test that _execute_query method correctly calls the collection.query method
        with the expected parameters and returns the query result.
        """
        # Setup
        options = ChromaDBRetrieverOptions(
            persist_directory="test_dir",
            collection_name="test_collection",
            n_results=5
        )
        retriever = ChromaDBRetriever(options)

        # Mock the collection
        retriever.collection = Mock()
        expected_result = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [{"meta1": "value1"}, {"meta2": "value2"}],
            "distances": [[0.1, 0.2]]
        }
        retriever.collection.query.return_value = expected_result

        # Execute
        result = retriever._execute_query("test query")

        # Assert
        retriever.collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        self.assertEqual(result, expected_result)

    def test__execute_query_collection_not_found(self):
        """
        Test the _execute_query method when the collection is not found.
        This should raise an exception (exact type depends on ChromaDB implementation).
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="non_existent_collection")
        retriever = ChromaDBRetriever(options)
        retriever.collection = Mock()
        retriever.collection.query.side_effect = Exception("Collection not found")

        with pytest.raises(Exception):
            retriever._execute_query("test query")

    def test__execute_query_connection_error(self):
        """
        Test the _execute_query method when there's a connection error to the ChromaDB.
        This should raise an exception (exact type depends on ChromaDB implementation).
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        retriever.collection = Mock()
        retriever.collection.query.side_effect = Exception("Connection error")

        with pytest.raises(Exception):
            retriever._execute_query("test query")

    def test__execute_query_empty_input(self):
        """
        Test the _execute_query method with an empty input string.
        This should raise a ValueError as empty queries are not allowed.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        retriever.collection = Mock()

        with pytest.raises(ValueError):
            retriever._execute_query("")

    def test__execute_query_non_string_input(self):
        """
        Test the _execute_query method with a non-string input (e.g., an integer).
        This should raise a TypeError as the method expects a string.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        retriever.collection = Mock()

        with pytest.raises(TypeError):
            retriever._execute_query(123)

    def test__execute_query_none_input(self):
        """
        Test the _execute_query method with None as input.
        This should raise a TypeError as the method expects a string.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        retriever.collection = Mock()

        with pytest.raises(TypeError):
            retriever._execute_query(None)

    def test_retrieve_3(self):
        """
        Test the retrieve method when results are not empty but similarity score is below threshold.

        This test verifies that the retrieve method returns an empty list when the
        similarity score of all results is below the similarity threshold, even though
        the query returns non-empty results.
        """
        # Setup
        options = ChromaDBRetrieverOptions(
            persist_directory="test_dir",
            collection_name="test_collection",
            n_results=2,
            similarity_threshold=0.8
        )
        retriever = ChromaDBRetriever(options)

        # Mock the _execute_query method to return non-empty results
        async def mock_execute_query(text):
            return {
                'documents': [['doc1', 'doc2']],
                'metadatas': [[{'meta1': 'value1'}, {'meta2': 'value2'}]],
                'distances': [[0.3, 0.4]]  # These will result in similarity scores below the threshold
            }
        retriever._execute_query = mock_execute_query

        # Execute the retrieve method
        result = asyncio.run(retriever.retrieve("test query"))

        # Assert that the result is an empty list
        assert result == []

    def test_retrieve_and_combine_results_2(self):
        """
        Test the retrieve_and_combine_results method when results are present.

        This test verifies that the method correctly combines the content,
        prepares the sources, and returns the expected dictionary structure
        when there are retrieval results.
        """
        # Create a mock ChromaDBRetriever instance
        retriever = ChromaDBRetriever(ChromaDBRetrieverOptions(
            persist_directory="test_dir",
            collection_name="test_collection"
        ))

        # Mock the retrieve method to return non-empty results
        retriever.retrieve = AsyncMock(return_value=[
            {
                'content': 'Content 1',
                'metadata': {'source': 'Source 1'},
                'similarity_score': 0.9
            },
            {
                'content': 'Content 2',
                'metadata': {'source': 'Source 2'},
                'similarity_score': 0.8
            }
        ])

        # Call the method and get the result
        result = pytest.run_async(retriever.retrieve_and_combine_results("test query"))

        # Assert the expected structure and content of the result
        assert result == {
            "combined_content": "Content 1\n\nContent 2",
            "sources": [
                {"metadata": {'source': 'Source 1'}, "similarity_score": 0.9},
                {"metadata": {'source': 'Source 2'}, "similarity_score": 0.8}
            ],
            "total_sources": 2
        }

        # Verify that retrieve was called with the correct argument
        retriever.retrieve.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_retrieve_and_combine_results_empty(self):
        """
        Test the retrieve_and_combine_results method when no results are returned.

        This test verifies that when the retrieve method returns an empty list,
        the retrieve_and_combine_results method correctly handles this scenario
        by returning a dictionary with empty content, no sources, and a total
        source count of 0.
        """
        # Setup
        options = ChromaDBRetrieverOptions(
            persist_directory="test_dir",
            collection_name="test_collection"
        )
        retriever = ChromaDBRetriever(options)

        # Mock the retrieve method to return an empty list
        retriever.retrieve = lambda _: []

        # Execute the method
        result = await retriever.retrieve_and_combine_results("test query")

        # Assert the expected outcome
        assert result == {
            "combined_content": "",
            "sources": [],
            "total_sources": 0
        }

    @pytest.mark.asyncio
    async def test_retrieve_and_combine_results_empty_input(self):
        """
        Test case for empty input to retrieve_and_combine_results method.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)

        result = await retriever.retrieve_and_combine_results("")

        assert result == {
            "combined_content": "",
            "sources": [],
            "total_sources": 0
        }

    @pytest.mark.asyncio
    async def test_retrieve_and_combine_results_exception_handling(self):
        """
        Test case for exception handling in retrieve_and_combine_results method.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)

        # Simulate an exception by setting the collection to None
        retriever.collection = None

        result = await retriever.retrieve_and_combine_results("test query")

        assert result == {
            "combined_content": "",
            "sources": [],
            "total_sources": 0
        }

    @pytest.mark.asyncio
    async def test_retrieve_and_combine_results_incorrect_input_type(self):
        """
        Test case for incorrect input type to retrieve_and_combine_results method.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)

        with pytest.raises(TypeError):
            await retriever.retrieve_and_combine_results(123)

    @pytest.mark.asyncio
    async def test_retrieve_and_combine_results_no_results(self):
        """
        Test case for when retrieve method returns no results.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)

        # Mock the retrieve method to return an empty list
        retriever.retrieve = lambda _: []

        result = await retriever.retrieve_and_combine_results("test query")

        assert result == {
            "combined_content": "",
            "sources": [],
            "total_sources": 0
        }

    async def test_retrieve_and_generate_2(self):
        """
        Test the retrieve_and_generate method when combined_results['combined_content'] is not empty.

        This test verifies that the method correctly processes and returns the expected output
        when there are valid combined results from the retrieval process.
        """
        # Setup
        options = ChromaDBRetrieverOptions(
            persist_directory="test_persist_dir",
            collection_name="test_collection"
        )
        retriever = ChromaDBRetriever(options)

        # Mock the retrieve_and_combine_results method
        async def mock_retrieve_and_combine_results(text: str) -> Dict[str, Any]:
            return {
                "combined_content": "First paragraph.\n\nSecond paragraph.",
                "sources": [{"metadata": {"source": "test"}, "similarity_score": 0.9}],
                "total_sources": 1
            }
        retriever.retrieve_and_combine_results = mock_retrieve_and_combine_results

        # Execute the method
        result = await retriever.retrieve_and_generate("test query")

        # Assert the results
        assert result["generated_content"] == "First paragraph.\n\nSecond paragraph."
        assert result["summary"] == "First paragraph."
        assert result["sources"] == [{"metadata": {"source": "test"}, "similarity_score": 0.9}]
        assert result["total_sources"] == 1

    @pytest.mark.asyncio
    async def test_retrieve_and_generate_empty_combined_content(self):
        """
        Test retrieve_and_generate with empty combined_content but non-empty sources.
        This should return an empty result dictionary.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        retriever.retrieve_and_combine_results = AsyncMock(return_value={
            "combined_content": "",
            "sources": [{"metadata": {}, "similarity_score": 0.8}],
            "total_sources": 1
        })

        result = await retriever.retrieve_and_generate("test input")

        assert result == {
            "generated_content": "",
            "summary": "",
            "sources": [],
            "total_sources": 0
        }

    @pytest.mark.asyncio
    async def test_retrieve_and_generate_empty_input(self):
        """
        Test retrieve_and_generate with empty input.
        This should return an empty result dictionary.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        retriever.retrieve_and_combine_results = AsyncMock(return_value={
            "combined_content": "",
            "sources": [],
            "total_sources": 0
        })

        result = await retriever.retrieve_and_generate("")

        assert result == {
            "generated_content": "",
            "summary": "",
            "sources": [],
            "total_sources": 0
        }

    @pytest.mark.asyncio
    async def test_retrieve_and_generate_empty_results(self):
        """
        Test retrieve_and_generate method when no results are found.

        This test verifies that when the retrieve_and_combine_results method
        returns empty results, the retrieve_and_generate method correctly
        handles this scenario by returning a dictionary with empty values.
        """
        # Setup
        options = ChromaDBRetrieverOptions(
            persist_directory="test_persist",
            collection_name="test_collection"
        )
        retriever = ChromaDBRetriever(options)

        # Mock the retrieve_and_combine_results method to return empty results
        async def mock_retrieve_and_combine_results(text):
            return {
                "combined_content": "",
                "sources": [],
                "total_sources": 0
            }
        retriever.retrieve_and_combine_results = mock_retrieve_and_combine_results

        # Execute
        result = await retriever.retrieve_and_generate("test query")

        # Assert
        expected_result = {
            "generated_content": "",
            "summary": "",
            "sources": [],
            "total_sources": 0
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_retrieve_and_generate_exception_handling(self):
        """
        Test retrieve_and_generate exception handling.
        This should return an empty result dictionary when an exception occurs.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        retriever.retrieve_and_combine_results = AsyncMock(side_effect=Exception("Test exception"))

        result = await retriever.retrieve_and_generate("test input")

        assert result == {
            "generated_content": "",
            "summary": "",
            "sources": [],
            "total_sources": 0
        }

    @pytest.mark.asyncio
    async def test_retrieve_and_generate_incorrect_input_type(self):
        """
        Test retrieve_and_generate with incorrect input type.
        This should raise a TypeError.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)

        with pytest.raises(TypeError):
            await retriever.retrieve_and_generate(123)

    def test_retrieve_below_similarity_threshold(self):
        """
        Test the retrieve method when all results are below the similarity threshold.
        Expect an empty list to be returned.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection", similarity_threshold=0.8)
        retriever = ChromaDBRetriever(options)

        # Mock the _execute_query method to return results with low similarity scores
        def mock_execute_query(*args):
            return {
                'documents': [['doc1', 'doc2']],
                'metadatas': [[{'meta1': 'value1'}, {'meta2': 'value2'}]],
                'distances': [[0.3, 0.4]]
            }

        retriever._execute_query = mock_execute_query

        result = asyncio.run(retriever.retrieve("test query"))
        assert result == []

    def test_retrieve_empty_input(self):
        """
        Test the retrieve method with an empty input string.
        Expect an empty list to be returned.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        result = asyncio.run(retriever.retrieve(""))
        assert result == []

    @pytest.mark.asyncio
    async def test_retrieve_empty_results(self):
        """
        Test the retrieve method when the query results are empty.
        This test verifies that the method returns an empty list when no documents are found.
        """
        # Setup
        options = ChromaDBRetrieverOptions(
            persist_directory="test_dir",
            collection_name="test_collection",
            n_results=5,
            similarity_threshold=0.7
        )
        retriever = ChromaDBRetriever(options)

        # Mock the _execute_query method to return empty results
        with patch.object(retriever, '_execute_query') as mock_execute_query:
            mock_execute_query.return_value = {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

            # Execute the method
            result = await retriever.retrieve("test query")

            # Assert
            assert result == [], "Expected an empty list when no documents are found"
            mock_execute_query.assert_called_once_with("test query")

    def test_retrieve_exception_handling(self):
        """
        Test the exception handling in the retrieve method.
        Simulate an exception and expect an empty list to be returned.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)

        # Mock the _execute_query method to raise an exception
        def mock_execute_query(*args):
            raise Exception("Simulated error")

        retriever._execute_query = mock_execute_query

        result = asyncio.run(retriever.retrieve("test query"))
        assert result == []

    def test_retrieve_invalid_input_type(self):
        """
        Test the retrieve method with an invalid input type (int instead of str).
        Expect a TypeError to be raised.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)
        with pytest.raises(TypeError):
            asyncio.run(retriever.retrieve(123))

    def test_retrieve_no_results(self):
        """
        Test the retrieve method when no results are returned from the query.
        Expect an empty list to be returned.
        """
        options = ChromaDBRetrieverOptions(persist_directory="test_dir", collection_name="test_collection")
        retriever = ChromaDBRetriever(options)

        # Mock the _execute_query method to return no results
        def mock_execute_query(*args):
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

        retriever._execute_query = mock_execute_query

        result = asyncio.run(retriever.retrieve("test query"))
        assert result == []

    @pytest.mark.asyncio
    async def test_retrieve_with_valid_results_and_high_similarity(self):
        """
        Test the retrieve method when valid results are returned and similarity score is above the threshold.

        This test verifies that:
        1. The retrieve method handles non-empty results correctly.
        2. It properly calculates similarity scores.
        3. It filters results based on the similarity threshold.
        4. It formats the results as expected.
        """
        # Mock ChromaDBRetriever and its dependencies
        options = ChromaDBRetrieverOptions(
            persist_directory="test_dir",
            collection_name="test_collection",
            n_results=2,
            similarity_threshold=0.7
        )
        retriever = ChromaDBRetriever(options)

        # Mock the _execute_query method to return predetermined results
        async def mock_execute_query(text):
            return {
                'documents': [['doc1', 'doc2']],
                'metadatas': [[{'meta1': 'value1'}, {'meta2': 'value2'}]],
                'distances': [[0.2, 0.4]]
            }

        retriever._execute_query = mock_execute_query

        # Call the retrieve method
        results = await retriever.retrieve("test query")

        # Assert the results
        assert len(results) == 2
        assert results[0]['content'] == 'doc1'
        assert results[0]['metadata'] == {'meta1': 'value1'}
        assert results[0]['similarity_score'] == pytest.approx(0.8)
        assert results[1]['content'] == 'doc2'
        assert results[1]['metadata'] == {'meta2': 'value2'}
        assert results[1]['similarity_score'] == pytest.approx(0.6)