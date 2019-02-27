def update_doc_with_invalid_hype_hint(doc: str):
    postfix = '(Note: parameter type can be wrong)'
    separator = ' ' if doc else ''
    return separator.join((doc, postfix))
