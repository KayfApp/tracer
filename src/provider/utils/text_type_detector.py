from enum import Enum
import re

class TextType(Enum):
    """
    Enumeration representing different types of text formats.

    Attributes:
        PLAIN: Represents plain text with no formatting.
        MARKDOWN: Represents text formatted in Markdown.
        HTML: Represents text formatted in HTML.
    """
    PLAIN = 1
    MARKDOWN = 2
    HTML = 3

def detect_text_type(text: str) -> TextType:
    """
    Detects the type of text format (plain, Markdown, or HTML).

    This function analyzes the provided text to determine its format based 
    on specific patterns and tags associated with HTML and Markdown. 
    It uses regular expressions to identify common elements in HTML 
    and Markdown.

    Parameters:
    text (str): The input text string to be analyzed for format detection.

    Returns:
    TextType: An enumeration value indicating the detected text type:
        - TextType.PLAIN: If the text does not match any Markdown or HTML patterns.
        - TextType.MARKDOWN: If the text matches common Markdown patterns.
        - TextType.HTML: If the text matches common HTML tags.

    Example:
    >>> detect_text_type("<p>This is a paragraph.</p>")
    <TextType.HTML: 3>

    >>> detect_text_type("# This is a header")
    <TextType.MARKDOWN: 2>

    >>> detect_text_type("This is plain text.")
    <TextType.PLAIN: 1>
    """
    # Simple HTML detection using common tags
    html_pattern = re.compile(r"</?(html|head|body|div|span|p|h[1-6]|a|img|ul|ol|li|table|tr|td|th|strong|em|br|hr|script|style|meta|link)[^>]*>", re.IGNORECASE)
    
    # Simple Markdown detection using common Markdown patterns
    markdown_patterns = [
        r"^\#{1,6}\s",  # Headers (#, ##, ### ...)
        r"\*\*.*?\*\*",  # Bold (**bold**)
        r"\*.*?\*",      # Italics (*italics*)
        r"__.*?__",      # Bold (__bold__)
        r"_.*?_",        # Italics (_italics_)
        r"!\[.*?\]\(.*?\)",  # Images ![alt](url)
        r"\[.*?\]\(.*?\)",   # Links [text](url)
        r"^\>\s",       # Blockquotes (>)
        r"^\d+\.\s",    # Ordered lists (1. Item)
        r"^-{3,}$",     # Horizontal rule (--- or ***)
    ]
    
    # Check for HTML patterns
    if html_pattern.search(text):
        return TextType.HTML
    
    # Check for Markdown patterns
    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return TextType.MARKDOWN
    
    # If neither HTML nor Markdown patterns are found, return PLAIN
    return TextType.PLAIN
