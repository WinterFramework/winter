from typing import Optional

import docstring_parser


class Docstring:

    def __init__(self, doc: str):
        self._docstring = docstring_parser.parse(doc)
        self.params_docs = {param_doc.arg_name: param_doc for param_doc in self._docstring.params}

    @property
    def short_description(self) -> Optional[str]:
        return self._docstring.short_description

    @property
    def long_description(self) -> Optional[str]:
        return self._docstring.long_description

    def get_description(self) -> Optional[str]:
        blank_line = self._docstring.blank_after_short_description and '\n' or ''
        long_description = self.long_description and f'\n{blank_line}{self.long_description}' or ''
        return self.short_description and self.short_description + long_description

    def get_argument_description(self, argument_name: str) -> str:
        param_doc = self.params_docs.get(argument_name)
        description = param_doc.description if param_doc is not None else ''

        return description
