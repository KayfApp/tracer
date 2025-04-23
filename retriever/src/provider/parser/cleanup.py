from provider.parser.markup_parser import html_to_plain, markdown_to_plain
from provider.utils.text_type_detector import TextType, detect_text_type

def clean_up(content: str) -> str:
    ft = detect_text_type(content)
    if ft == TextType.HTML:
        content = html_to_plain(content)
    elif ft == TextType.MARKDOWN:
        content = markdown_to_plain(content)
    return content
