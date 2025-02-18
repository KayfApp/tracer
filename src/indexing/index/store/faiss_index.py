import gc
import math
import os
from typing import List, Optional, Set
import threading

import faiss
import numpy as np
import torch
from context import Context
from env import EMBEDDING_DIMS
from error.not_loaded_error import NotLoadedError
from globals import EMBEDDING_ENCODER
from indexing.index.generic_index import GenericIndex, SearchResult
from provider.utils.pipeline import ProcessedDocument

class FaissIndex(GenericIndex):
    _NAME: str = "FAISS"
    _EXT: str = "faiss"

    def __init__(self, path: str, **kwargs):
        super().__init__(path)
        self._index = None
        self._is_clustered = False
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._size: float = 0
        self._ids: Set[int] = set()
        self._lock = threading.Lock()  # Lock for thread safety
        self._context: Set[Context] = set()

    def load(self, context : Optional[Context] = None) -> None:
        with self._lock:
            if context:
                self._context.add(context)

            if self._index != None:
                return

            if os.path.exists(self._path):
                self._index = faiss.read_index(self._path)
                if isinstance(self._index, faiss.IndexIVFFlat):
                    self._is_clustered = True
                
                metadata_store = torch.load(f"{self._path}.metadata")
                self._size = metadata_store['size']
                self._ids = metadata_store['ids']
            else:
                base_index = faiss.IndexFlatIP(EMBEDDING_DIMS)
                self._index = faiss.IndexIDMap2(base_index)
                self._size = 0
                self._ids = set()

    def release(self, context: Optional[Context] = None) -> None:
        with self._lock:
            if context:
                self._context.discard(context)
                context.free()

            if not self._context:
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

    def has_id(self, id: int) -> bool:
        return id in self._ids

    def id_intersection(self, ids: Set[int]) -> Set[int]:
        return ids & self._ids

    def insert(self, documents: List[ProcessedDocument]) -> None:
        with self._lock:
            if self._index == None:
                raise NotLoadedError(f"Index with path {self._path} not loaded!")

            embeddings = EMBEDDING_ENCODER.encode([document.data for document in documents], convert_to_numpy=True).astype('float32')
            ids_list = [document.id for document in documents]
            ids = np.array(ids_list).astype('int64')
            faiss.normalize_L2(embeddings)
            self._index.add_with_ids(embeddings, ids) #pyright: ignore
            self._ids.update(ids_list)

    def remove(self, ids: List[int]) -> None:
        with self._lock:
            if self._index == None:
                raise NotLoadedError(f"Index with path {self._path} not loaded!")

            np_ids = np.array(ids).astype('int64')
            self._index.remove_ids(np_ids)
            for id in ids:
                self._ids.discard(id)

    def save(self, path: Optional[str] = None) -> None:
        with self._lock:
            faiss.write_index(self._index, path != None and self._path)
            torch.save({
                'size': self._size,
                'ids': self._ids
            }, f"{self._path}.metadata")

    @property
    def size(self) -> float:
        with self._lock:
            if self._index != None:
                self._size = 0
                dim = EMBEDDING_DIMS
                len = self._index.ntotal
                # vector size
                self._size = 4 * dim * len # overhead
                if isinstance(self._index, faiss.IndexIVFFlat):
                    clusters = self._index.nlist
                    self._size += clusters * dim * 4
                    self._size += len * 4 * 4

            return self._size/(1024**2)


    @property
    def max_doc_size(self) -> float:
        return (4 * EMBEDDING_DIMS)/(1024**2)
 
    def capacity(self, max_index_size: float) -> int:
        curr_size = self.size
        max_doc_size = self.max_doc_size
        return max(0, int((max_index_size - curr_size)/max_doc_size))        

    def cluster(self, cluster_n: int) -> None:
        with self._lock:
            if self._index is None:
                raise NotLoadedError(f"Index with path {self._path} not loaded!")
            
            len = self._index.ntotal
            dim = EMBEDDING_DIMS

            if len > 0 and not isinstance(self._index, faiss.IndexIVFFlat):
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
