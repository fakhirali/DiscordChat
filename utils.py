import re

def truncate_message(message):
    # split the message into sentences
    sentences = message.split('.')
    while len('.'.join(sentences)) > 1900:
        sentences.pop()
    return '.'.join(sentences)


def remove_mentions(text):
    # Remove text inside <>
    cleaned_text = re.sub("<[^>]*>", "", text)
    return cleaned_text