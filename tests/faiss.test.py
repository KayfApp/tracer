import unittest
import os
import sys
import faiss

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from env import EMBEDDING_DIMS
from indexing.index.store.faiss_index import FaissIndex
from schema.document.sub_document import SubDocument
from error.not_loaded_error import NotLoadedError
from indexing.index.generic_index import SearchResult

class TestFaissIndex(unittest.TestCase):

    def setUp(self):
        self.test_index_path = "test_index.faiss"
        if os.path.exists(self.test_index_path):
            os.remove(self.test_index_path)
        self.faiss_index = FaissIndex(self.test_index_path)
        self.sample_documents = [
            SubDocument(id=1, data="The library for the robotics competition will be implemented in C++."),
            SubDocument(id=2, data="Brother smoked some weed in the garden bro.."),
            SubDocument(id=3, data="Congratulations! You qualified for the International Olympiad of Informatics!")
        ]

    def tearDown(self):
        if os.path.exists(self.test_index_path):
            os.remove(self.test_index_path)

    def test_load_non_existent_index(self):
        self.faiss_index.load()
        self.assertIsNotNone(self.faiss_index._index)
        self.assertFalse(self.faiss_index._is_clustered)

    def test_load_existing_index(self):
        # Create a dummy index and save it
        base_index = faiss.IndexFlatIP(EMBEDDING_DIMS)
        dummy_index = faiss.IndexIDMap2(base_index)
        faiss.write_index(dummy_index, self.test_index_path)

        self.faiss_index.load()
        self.assertIsNotNone(self.faiss_index._index)
        self.assertFalse(self.faiss_index._is_clustered)

    def test_release(self):
        self.faiss_index.load()
        self.faiss_index.release()
        self.assertIsNone(self.faiss_index._index)
        self.assertFalse(self.faiss_index._is_clustered)

    def test_search_without_loading(self):
        with self.assertRaises(NotLoadedError):
            self.faiss_index.search("query", k=1)

    def test_search(self):
        self.faiss_index.load()
        self.assertFalse(self.faiss_index._is_clustered)
        self.faiss_index.insert(self.sample_documents)
        results = self.faiss_index.search("Competition Olympiad", k=2)
        self.assertEqual(len(results), 2)
        self.faiss_index.release()
        self.faiss_index.load()
        self.assertFalse(self.faiss_index._is_clustered)
        self.assertTrue(all(isinstance(result, SearchResult) for result in results))

    def test_insert_without_loading(self):
        with self.assertRaises(NotLoadedError):
            self.faiss_index.insert(self.sample_documents)

    def test_insert(self):
        self.faiss_index.load()
        self.faiss_index.insert(self.sample_documents)
        self.assertEqual(self.faiss_index._index.ntotal, len(self.sample_documents))

    def test_remove_without_loading(self):
        with self.assertRaises(NotLoadedError):
            self.faiss_index.remove([1, 2])

    def test_remove(self):
        self.faiss_index.load()
        self.faiss_index.insert(self.sample_documents)
        self.faiss_index.remove([1, 2])
        self.assertEqual(self.faiss_index._index.ntotal, 1)

    def test_save(self):
        self.faiss_index.load()
        self.faiss_index.insert(self.sample_documents)
        self.faiss_index.save(self.test_index_path)
        self.assertTrue(os.path.exists(self.test_index_path))

    def test_size(self):
        self.faiss_index.load()
        self.faiss_index.insert(self.sample_documents)
        size = self.faiss_index.size
        self.assertGreater(size, 0)

    def test_cluster_without_loading(self):
        with self.assertRaises(NotLoadedError):
            self.faiss_index.cluster(cluster_n=2)

    def test_cluster(self):
        self.faiss_index.load()
        self.faiss_index.insert(self.sample_documents)
        self.faiss_index.cluster(cluster_n=2)
        self.assertTrue(self.faiss_index._is_clustered)
        self.faiss_index.save(self.test_index_path)
        self.faiss_index.release()
        self.faiss_index.load()
        self.assertTrue(self.faiss_index._is_clustered)


    def test_name(self):
        self.assertEqual(FaissIndex.name(), "FAISS")

    def test_extension(self):
        self.assertEqual(FaissIndex.extension(), "faiss")

if __name__ == "__main__":
    unittest.main()
