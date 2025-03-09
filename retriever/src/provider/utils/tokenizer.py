import re
from typing import List
from nltk.tokenize import sent_tokenize, word_tokenize

def clean_text(text: str) -> str:
    """
    Cleans input text by removing extra whitespace, adjusting spacing around punctuation,
    and removing carriage returns, newlines, and tabs.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.

    Example:
        >>> clean_text("  Hello,   world!  ")
        'Hello, world!'
    """

    # Remove non-printable/control Unicode characters (e.g., \u200c, \u200b, etc.)
    # \p{C} matches all Unicode "Other" categories (control, format, surrogate, etc.)
    text = re.sub(r'[\u0000-\u001F\u007F-\u009F\u200B-\u200F\u202A-\u202E]', '', text)
    # Remove carriage return, newline, and tab characters
    text = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

    # Clean extra spaces and adjust spacing around punctuation
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with one
    text = re.sub(r'\s*([,.!?;])\s*', r'\1 ', text)  # Adjust spaces around punctuation
    text = re.sub(r'\s*([,.!?;])', r'\1', text)  # Ensure no space before punctuation

    return text

def split_text_into_sentence_groups(text: str, token_limit: int) -> List[str]:
    """
    Splits input text into sentences and and groups them.

    Args:
        text (str): The text to split. It's recommended to replace the links with placeholders beforehand!
        token_limit (int): The maximum number of tokens per sentence chunk.

    Returns:
        - List of the grouped sentences.

    Example:
        >>> split_text_into_sentence_groups(("Hello! How are you? Visit PLACEHOLDER for more info.", 6)
        (['Hello! How are you?', 'Visit PLACEHOLDER for more info.'])
    """
    sentences: List[str] = sent_tokenize(text)

    sentence_groups: List[str] = []

    curr_sentence_group: List[str] = []
    curr_group_tokens = 0

    for sentence in sentences:
        # make sure that one individual sentence doesnt max out the token limit
        if len(sentence) <= token_limit:
            if curr_group_tokens + len(sentence) <= token_limit:
                curr_sentence_group.append(sentence)
                curr_group_tokens += len(sentence)
            else:
                sentence_groups.append(' '.join(curr_sentence_group))
                curr_group_tokens = len(sentence)
                curr_sentence_group = [sentence]
        else:
            words = word_tokenize(sentence)
            if curr_group_tokens:
                sentence_groups.append(' '.join(curr_sentence_group))
                curr_group_tokens = len(words)
                curr_sentence_group = []

            for word in words:
                if curr_group_tokens + len(word) <= token_limit:
                    curr_sentence_group.append(word)
                    curr_group_tokens += len(word)
                else:
                    sentence_groups.append(' '.join(curr_sentence_group))
                    curr_group_tokens = len(word)
                    curr_sentence_group = [word]


    if curr_sentence_group:
        sentence_groups.append(' '.join(curr_sentence_group))

    return sentence_groups
