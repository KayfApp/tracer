import asyncio
from googletrans import Translator

async def translator(text: str, dest: str) -> str:
    """
    Asynchronously translates text to a specified language.

    This function uses the Google Translate API to perform translation. 
    It establishes an asynchronous context with the Translator, 
    translates the input text to the desired destination language, 
    and returns the translated text.

    Parameters:
    text (str): The text string to be translated.
    dest (str): The language code for the target language (e.g., 'en' for English, 'fr' for French).

    Returns:
    str: The translated text in the specified destination language.

    Example:
    >>> asyncio.run(translator("Hello, world!", "es"))
    '¡Hola, mundo!'
    """
    async with Translator(service_urls=['translate.googleapis.com']) as translator:
        result = await translator.translate(text, dest=dest)
        return result.text

def translate_to(text: str, dest: str) -> str:
    """
    Translates text to a specified language using synchronous execution.

    This function serves as a wrapper around the asynchronous `translator` function.
    It runs the asynchronous translation function using `asyncio.run`, 
    allowing synchronous code to call it.

    Parameters:
    text (str): The text string to be translated.
    dest (str): The language code for the target language.

    Returns:
    str: The translated text in the specified destination language.

    Example:
    >>> translate_to("Good morning!", "fr")
    'Bonjour!'
    """
    return asyncio.run(translator(text, dest))

def translate_to_english(text: str) -> str:
    """
    Translates text to English.

    This function provides a convenient way to translate any given 
    text directly to English by calling the `translate_to` function 
    with 'en' as the destination language.

    Parameters:
    text (str): The text string to be translated to English.

    Returns:
    str: The translated text in English.

    Example:
    >>> translate_to_english("Hola, mundo!")
    'Hello, world!'
    """
    return translate_to(text, 'en')
