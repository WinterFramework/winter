import docstring_parser


class DocstringParser:

    def __init__(self, doc: str):
        docstring = docstring_parser.parse(doc)
        self.params_docs = {param_doc.arg_name: param_doc for param_doc in docstring.params}

    def get_description(self, argument_name: str, invalid_type_hint: bool = False):
        param_doc = self.params_docs.get(argument_name)
        description = param_doc.description if param_doc is not None else ''

        if invalid_type_hint:
            description = self.update_doc_with_invalid_hype_hint(description)
        return description

    def update_doc_with_invalid_hype_hint(self, doc: str):
        postfix = '(Note: parameter type can be wrong)'
        separator = ' ' if doc else ''
        return separator.join((doc, postfix))
