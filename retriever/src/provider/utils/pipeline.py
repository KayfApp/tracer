from datetime import datetime
import re
from typing import List
from globals import DB_SESSION
from provider.utils.tokenizer import clean_text, split_text_into_sentence_groups
from provider.utils.translator import translate_to_english
from env import EMBEDDING_TOKEN_LIMIT
from schema.connections.provider_instance import ProviderInstance
from schema.document.document import Document
from schema.document.sub_document import SubDocument

class ProcessedDocument():
    def __init__(self, id: int, data: str):
        self._id = id
        self._data = data

    @property
    def id(self):
        """The id property."""
        return self._id
    
    @property
    def data(self):
        """The data property."""
        return self._data

def pipeline(content: str,
             provider_instance_id: int,
             doc_type: str,
             status: str,
             title: str,
             author: str,
             author_avatar: str,
             url: str,
             location: str,
             timestamp: datetime
             ) -> List[ProcessedDocument]:
    """
    Process raw document content into structured sub-documents stored in a database.

    This function performs the following steps:
    1. Extracts and replaces URLs with placeholders.
    2. Translates text to English.
    3. Splits text into token-limited sentence groups.
    4. Reinserts original URLs into processed text.
    5. Persists documents and sub-documents in the database.
    6. Returns processed sub-documents with database IDs and cleaned text.

    Args:
        content: Raw input text (may contain HTML/Markdown formatting and URLs)
        provider_instance_id: Database ID of the data provider instance
        doc_type: Type classification of the document
        status: Document status (e.g., 'processed', 'archived')
        title: Document title
        author: Author name
        author_avatar: URL to author's avatar image
        url: Source URL of the document
        location: Geographic location associated with the document
        timestamp: Publication/creation datetime

    Returns:
        List[ProcessedDocument]: Processed sub-documents containing:
            - Database ID from persisted SubDocument
            - Cleaned text content without URLs

    Processing Details:
        - URLs are extracted and replaced with LINK_PLACEHOLDER during initial processing
        - Content is converted to plain text (HTML/Markdown removed)
        - Text is translated to English using `translate_to_english`
        - Cleaned text is split into chunks using token limits from TOKENIZER
        - Original URLs are reinserted into appropriate positions
        - Documents and sub-documents are persisted to the database
        - Returns sub-document data both with and without URLs for different use cases
    """

    # Store and remove links
    links = re.findall(r'https?://\S+|www\.\S+', content)
    content = re.sub(r'https?://\S+|www\.\S+', 'LINK_PLACEHOLDER', content)
    
    content = translate_to_english(clean_text(content))
    sentences = split_text_into_sentence_groups(content, EMBEDDING_TOKEN_LIMIT)


    # Remove placeholders
    sentences_without_links = [group.replace('LINK_PLACEHOLDER', '') for group in sentences]

    current_link_idx = 0
    sentences_with_links = []

    # Insert links instead of placeholders
    for group in sentences:
        parts = group.split('LINK_PLACEHOLDER')
        reconstructed: List[str] = []
        for i in range(len(parts)):
            reconstructed.append(parts[i])
            if i < len(parts) - 1:
                if current_link_idx < len(links):
                    reconstructed.append(links[current_link_idx])
                    current_link_idx += 1
                else:
                    # Handle unexpected placeholder without a corresponding link
                    reconstructed.append('')
        sentences_with_links.append(' '.join(reconstructed))

    # Insert everything into place
    sub_docs: List[SubDocument] = []
    processed_documents: List[ProcessedDocument] = []

    with DB_SESSION() as session:
        origin = session.query(ProviderInstance).filter_by(id=provider_instance_id).first()
        doc = Document(doc_type=doc_type, status=status, title=title, author=author, author_avatar=author_avatar, url=url, location=location, timestamp=timestamp, origin=origin)  
        session.add(doc)

        for sentence in sentences_with_links:
            sub_doc = SubDocument(data=sentence, document=doc)
            sub_docs.append(sub_doc)
            session.add(sub_doc)
            
        session.commit()
       # Refresh sub-documents to load ids and re-attach them to the session
        for sub_doc in sub_docs:
            session.refresh(sub_doc)

    # Processed documents are created in the aftermath due to the DB commit assigning ids
    for idx, sub_doc in enumerate(sub_docs):
        processed_documents.append(ProcessedDocument(sub_doc.id, sentences_without_links[idx]))
 
    return processed_documents
