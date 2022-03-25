from PyQt5.QtWidgets import QLineEdit


def get_text_or_placeholder_text(text_widget: QLineEdit) -> str:
    """If a text is present, that is not '', grab the text, else, grab the placeholder text."""
    if text_widget.text() != '':
        return text_widget.text()
    else:
        return text_widget.placeholderText()
