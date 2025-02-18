import os
import math
import torch
from collections import Counter
from typing import Dict, List, Optional

from indexing.index.generic_index import GenericIndex, SearchResult
from schema.document.sub_document import SubDocument

class BM25Index(GenericIndex):
    _NAME: str = "BM25"
    _EXT: str = "bm25"

    def __init__(self, path: str, **kwargs):
        super().__init__(path)
        self.k = kwargs.get("k", 1.5)
        self.b = kwargs.get("b", 0.7)
        self.delta = kwargs.get("delta", 0)
     
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._documents: Optional[Dict[int, List[str]]] = None # Stores the documents tokenized on term level
        self._document_terms: Optional[Dict[str, int]] = None # The number of documents containing the term
        self._term_freqs: Optional[Dict[int, Dict[str, int]]] = None # The number of times a term appears in a document (index of list being the documents idx)
        self._avg_doc_len = 0
        self._N = 0
    
    def load(self) -> None:
        if os.path.exists(self._path):
            data = torch.load(self._path, map_location=self._device)
            self._documents = data["documents"]
            self._document_terms = data["document_terms"]
            self._term_freqs = data["term_freqs"]
            self._avg_doc_len = data["avg_doc_len"]
            self._N = len(self._documents)

    def release(self) -> None:
        self._documents = None
        self._document_terms = None


    def search(self, query: str, k: int) -> List[SearchResult]:
        scores: List[SearchResult] = []
        idf: Dict[str, float] = {}
        query_terms = query.split()

        for doc_id in self._documents:
            doc_score = 0.0
            for term in query_terms:
                if term not in idf:
                    idf[term] = self._idf(term)
                doc_score += idf[term] * self._tf(term, doc_id)
            scores.append(SearchResult(doc_id, doc_score))
        return sorted(scores, key=lambda x: x.score, reverse=True)[:k]

    def insert(self, documents: List[SubDocument]) -> None:
        delta_doc_len: int = 0

        for doc in documents:
            doc_id = doc.id

            if doc_id in self._documents:
                delta_doc_len -= len(self._documents[doc_id])
                terms = set(self._documents[doc_id])
                for term in terms:
                    self._document_terms[term] -= 1
                    if self._document_terms[term] <= 0:
                        self._document_terms.pop(term)

            delta_doc_len += len(doc.data)
            self._documents[doc_id] = doc.data.split()
            self._term_freqs[doc_id] = {}
            terms = Counter(self._documents[doc_id])
            
            for term in terms:
                self._term_freqs[doc_id][term] = terms[term]
                self._document_terms[term] = self._document_terms.get(term, 0) + 1               

            total_length = self._avg_doc_len * self._N + delta_doc_len
            self._N = len(self._documents)
            self._avg_doc_len = total_length / self._N

    def remove(self, ids: List[int]) -> None:
        for id in ids:
            terms = set(self._documents[id])
            for term in terms:
                self._document_terms[term] -= 1
                if self._document_terms[term] <= 0:
                    self._document_terms.pop(term)

            self._documents.pop(id)
            self._term_freqs.pop(id)

    def save(self, path: str | None) -> None:
        torch.save({
            "documents": self._documents,
            "document_terms": self._document_terms,
            "term_freqs": self._term_freqs,
            "avg_doc_len": self._avg_doc_len,
        }, path != None and path or self._path)

    @property
    def size(self) -> float:
        pass

    def cluster(self, cluster_n: int) -> None:
        raise AttributeError("Clustering not supported for BM25")

    @classmethod
    def name(cls) -> str:
        return cls._NAME

    @classmethod
    def extension(cls) -> str:
        return cls._EXT

    def _idf(self, term: str) -> float:
        df = self._document_terms.get(term, 0)
        return math.log((self._N + 1) / (df + 0.5))
    
    def _tf(self, term: str, doc_id: int) -> float:
        term_freq = self._term_freqs[doc_id][term]
        doc_len = len(self._documents[doc_id])

        numerator = (self.k + 1) * term_freq
        denominator = self.k * ((1 - self.b) + self.b * (doc_len/self._avg_doc_len))
        return numerator/denominator + self.delta
