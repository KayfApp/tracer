from bs4 import BeautifulSoup
import re
import markdown

def html_to_plain(html: str) -> str:
    """
    Converts HTML to a readable plain text format.

    This function processes an HTML string and converts it into a plain text format by:
    - Converting headings into "Heading: Content" format.
    - Converting lists into a plain text format (removing dashes or numbers).
    - Removing images.
    - Converting hyperlinks to "Text (URL)" format.

    Parameters:
    html (str): A string containing HTML content.

    Returns:
    str: A plain text representation of the input HTML, formatted for readability.
    
    Example:
    >>> html = "<h1>Title</h1><p>This is a paragraph.</p><ul><li>Item 1</li><li>Item 2</li></ul>"
    >>> print(html_to_plain(html))
    Title:
    This is a paragraph.
    Item 1
    Item 2
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Get all text from headings and replace them with "Heading: Content"
    for header in soup.find_all(re.compile("^h[1-6]$")):
        content = header.get_text(strip=True)
        if header.find_next_sibling():
            next_content = header.find_next_sibling().get_text(strip=True)
            header.replace_with(f"{content}: {next_content}\n")
        else:
            header.replace_with(f"{content}:\n")

    # Convert lists into plain text (no dashes or numbers)
    for ul in soup.find_all("ul"):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        ul.replace_with("\n".join(items) + "\n")

    for ol in soup.find_all("ol"):
        items = [li.get_text(strip=True) for li in ol.find_all("li")]
        ol.replace_with("\n".join(items) + "\n")

    # Convert links to "Text (URL)"
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        a.replace_with(f"{text} ({href})")

    # Remove images
    for img in soup.find_all("img"):
        img.extract()

    # Convert remaining HTML to plain text
    plain_text = soup.get_text(separator="\n", strip=True)

    # Replace multiple newlines with a single one
    plain_text = re.sub(r"\n\s*\n", "\n", plain_text)

    return plain_text

def markdown_to_plain(md: str) -> str:
    """
    Converts Markdown text to plain text format.

    This function first converts the provided Markdown string to HTML using the 
    markdown library, and then processes the resulting HTML with the 
    html_to_plain function to produce a plain text representation.

    Parameters:
    md (str): A string containing Markdown content.

    Returns:
    str: A plain text representation of the input Markdown, formatted for readability.
    
    Example:
    >>> md = "# Heading\n\n- List item 1\n- List item 2\n[Link](http://example.com)"
    >>> print(markdown_to_plain(md))
    Heading:
    List item 1
    List item 2
    Link (http://example.com)
    """
    html = markdown.markdown(md)
    return html_to_plain(html)
