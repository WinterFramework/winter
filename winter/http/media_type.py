from typing import Dict
from typing import NamedTuple

from typing import Tuple


class InvalidMediaTypeException(Exception):
    def __init__(self, media_type: str, message: str):
        super().__init__(f'{message}: {media_type}')
        self.media_type = media_type
        self.message = message


class MediaTypeParameter(NamedTuple):
    name: str
    value: str

    def __str__(self):
        return f'{self.name}={self.value}'


class MediaType(tuple):
    ALL: 'MediaType' = None
    APPLICATION_ATOM_XML: 'MediaType' = None
    APPLICATION_FORM_URLENCODED: 'MediaType' = None
    APPLICATION_JSON: 'MediaType' = None
    APPLICATION_JSON_UTF8: 'MediaType' = None
    APPLICATION_OCTET_STREAM: 'MediaType' = None
    APPLICATION_PDF: 'MediaType' = None
    APPLICATION_PROBLEM_JSON: 'MediaType' = None
    APPLICATION_PROBLEM_JSON_UTF8: 'MediaType' = None
    APPLICATION_PROBLEM_XML: 'MediaType' = None
    APPLICATION_RSS_XML: 'MediaType' = None
    APPLICATION_STREAM_JSON: 'MediaType' = None
    APPLICATION_XHTML_XML: 'MediaType' = None
    APPLICATION_XML: 'MediaType' = None
    IMAGE_GIF: 'MediaType' = None
    IMAGE_JPEG: 'MediaType' = None
    IMAGE_PNG: 'MediaType' = None
    MULTIPART_FORM_DATA: 'MediaType' = None
    TEXT_EVENT_STREAM: 'MediaType' = None
    TEXT_HTML: 'MediaType' = None
    TEXT_MARKDOWN: 'MediaType' = None
    TEXT_PLAIN: 'MediaType' = None
    TEXT_XML: 'MediaType' = None

    def __new__(cls, media_type_str: str):
        return tuple.__new__(cls, cls.parse(media_type_str))

    @property
    def type(self) -> str:
        return self[0]

    @property
    def subtype(self) -> str:
        return self[1]

    @property
    def parameters(self) -> Tuple[MediaTypeParameter]:
        return self[2]

    @staticmethod
    def parse(media_type: str) -> Tuple[str, str, Dict[str, str]]:
        media_type = media_type.strip()
        if not media_type:
            raise InvalidMediaTypeException(media_type, 'Media type must not be empty')
        parameters = []
        parts = media_type.split(';')
        for param_str in parts[1:]:
            key_value = param_str.strip().split('=')
            if len(key_value) != 2:
                raise InvalidMediaTypeException(media_type, 'Invalid media type parameter list')
            parameters.append(MediaTypeParameter(*key_value))
        full_type = parts[0]
        if full_type == '*':
            type_, subtype = '*', '*'
        else:
            full_type_parts = full_type.split('/')
            if len(full_type_parts) < 2:
                raise InvalidMediaTypeException(media_type, 'Media type must contain "/"')
            if len(full_type_parts) > 2:
                raise InvalidMediaTypeException(media_type, 'Invalid media type format')
            type_, subtype = full_type_parts
        if not type_:
            raise InvalidMediaTypeException(media_type, 'Empty type is specified')
        if not subtype:
            raise InvalidMediaTypeException(media_type, 'Empty subtype is specified')
        if (type_ == '*') != (subtype == '*'):
            raise InvalidMediaTypeException(media_type, 'Wildcard is allowed only in */* (all media types)')
        return type_, subtype, tuple(parameters)

    def __eq__(self, other) -> bool:
        if not isinstance(other, MediaType):
            return False
        return super().__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()

    def __str__(self) -> str:
        full_type = f'{self.type}/{self.subtype}'
        if self.parameters:
            return full_type + '; ' + '; '.join(str(parameter) for parameter in self.parameters)
        else:
            return full_type


MediaType.ALL = MediaType('*/*')
MediaType.APPLICATION_ATOM_XML = MediaType('application/atom+xml')
MediaType.APPLICATION_FORM_URLENCODED = MediaType('application/x-www-form-urlencoded')
MediaType.APPLICATION_JSON = MediaType('application/json')
MediaType.APPLICATION_JSON_UTF8 = MediaType('application/json; charset=utf-8')
MediaType.APPLICATION_OCTET_STREAM = MediaType('application/octet-stream')
MediaType.APPLICATION_PDF = MediaType('application/pdf')
MediaType.APPLICATION_PROBLEM_JSON = MediaType('application/problem+json')
MediaType.APPLICATION_PROBLEM_JSON_UTF8 = MediaType('application/problem; charset=utf-8')
MediaType.APPLICATION_PROBLEM_XML = MediaType('application/problem+xml')
MediaType.APPLICATION_RSS_XML = MediaType('application/rss+xml')
MediaType.APPLICATION_STREAM_JSON = MediaType('application/stream+json')
MediaType.APPLICATION_XHTML_XML = MediaType('application/xhtml+xml')
MediaType.APPLICATION_XML = MediaType('application/xml')
MediaType.IMAGE_GIF = MediaType('image/gif')
MediaType.IMAGE_JPEG = MediaType('image/jpeg')
MediaType.IMAGE_PNG = MediaType('image/png')
MediaType.MULTIPART_FORM_DATA = MediaType('multipart/form-data')
MediaType.TEXT_EVENT_STREAM = MediaType('text/event-stream')
MediaType.TEXT_HTML = MediaType('text/html')
MediaType.TEXT_MARKDOWN = MediaType('text/markdown')
MediaType.TEXT_PLAIN = MediaType('text/plain')
MediaType.TEXT_XML = MediaType('text/xml')
