import gc
import math
import os
from typing import List, Optional
import threading

import faiss
import numpy as np
import torch
from env import EMBEDDING_DIMS
from error.not_loaded_error import NotLoadedError
from globals import EMBEDDING_ENCODER
from indexing.index.generic_index import GenericIndex, SearchResult
from schema.document.sub_document import SubDocument

class FaissIndex(GenericIndex):
    _NAME: str = "FAISS"
    _EXT: str = "faiss"

    def __init__(self, path: str, **kwargs):
        super().__init__(path)
        self._index = None
        self._is_clustered = False
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._size = -1
        self._lock = threading.Lock()  # Lock for thread safety

    def load(self) -> None:
        with self._lock:
            if os.path.exists(self._path):
                self._index = faiss.read_index(self._path)
                if isinstance(self._index, faiss.IndexIVFFlat):
                    self._is_clustered = True
            else:
                base_index = faiss.IndexFlatIP(EMBEDDING_DIMS)
                self._index = faiss.IndexIDMap2(base_index)

    def release(self) -> None:
        with self._lock:
            self._index = None
            self._is_clustered = False
            gc.collect()

    def search(self, query: str, k: int) -> List[SearchResult]:
        with self._lock:
            if self._index == None:
                raise NotLoadedError(f"Index with path {self._path} not loaded!")

            query_embedding = EMBEDDING_ENCODER.encode([query], convert_to_numpy=True).astype('float32')
            faiss.normalize_L2(query_embedding)

            similarities, ids = self._index.search(query_embedding, k) #pyright:ignore
            similarities = torch.tensor(similarities[0]).to(self._device)
            normalized_scores = (similarities + 1)/2

            sorted_results = []
            for i in range(k):
                result = SearchResult(id=ids[0][i].item(), score=normalized_scores[i].item())
                sorted_results.append(result)

            return sorted_results

    def insert(self, documents: List[SubDocument]) -> None:
        with self._lock:
            if self._index == None:
                raise NotLoadedError(f"Index with path {self._path} not loaded!")

            embeddings = EMBEDDING_ENCODER.encode([document.data for document in documents], convert_to_numpy=True).astype('float32')
            ids = np.array([document.id for document in documents]).astype('int64')
            faiss.normalize_L2(embeddings)
            self._index.add_with_ids(embeddings, ids) #pyright: ignore

    def remove(self, ids: List[int]) -> None:
        with self._lock:
            if self._index == None:
                raise NotLoadedError(f"Index with path {self._path} not loaded!")

            np_ids = np.array(ids).astype('int64')
            self._index.remove_ids(np_ids)

    def save(self, path: Optional[str] = None) -> None:
        with self._lock:
            faiss.write_index(self._index, path != None and self._path)

    @property
    def size(self) -> float:
        with self._lock:
            if self._index != None:
                self._size = 0
                dim = self._index.d
                len = self._index.ntotal
                # vector size
                self._size = 4 * dim * len # overhead
                if self._is_clustered:
                    clusters = self._index.index.nlist
                    self._size += clusters * dim * 4
                    self._size += len * 4 * 4

            return self._size

    def cluster(self, cluster_n: int) -> None:
        with self._lock:
            if self._index is None:
                raise NotLoadedError(f"Index with path {self._path} not loaded!")
            
            len = self._index.ntotal
            dim = self._index.d

            if len > 0:
                quantizer = faiss.IndexFlatIP(dim)  # Use Inner Product (IP) as metric
                ivf_index = faiss.IndexIVFFlat(quantizer, dim, cluster_n, faiss.METRIC_INNER_PRODUCT)
                ids = faiss.vector_to_array(self._index.id_map)
                vectors = self._index.reconstruct_batch (ids) # pyright: ignore
    
                sample_size = min(len, len / (math.e ** (math.log10(len))) * (1 + math.log10(dim)))
        
                sample_vectors = torch.tensor(vectors).to(self._device)
        
                unique_vectors = torch.unique(sample_vectors, dim=0)
        
                if unique_vectors.shape[0] > sample_size:
                    indices = torch.randperm(unique_vectors.shape[0], device=self._device)[:sample_size]  # Randomly select
                    sample_vectors = unique_vectors[indices]
        
                ivf_index.train(sample_vectors.cpu().numpy()) #pyright: ignore
                ivf_index.add_with_ids(vectors, ids) #pyright: ignore
                self._index = ivf_index
                self._is_clustered = True
