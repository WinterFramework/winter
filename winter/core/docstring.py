import docstring_parser


class Docstring:

    def __init__(self, doc: str):
        docstring = docstring_parser.parse(doc)
        self.params_docs = {param_doc.arg_name: param_doc for param_doc in docstring.params}

    def get_argument_description(self, argument_name: str) -> str:
        param_doc = self.params_docs.get(argument_name)
        description = param_doc.description if param_doc is not None else ''

        return description
