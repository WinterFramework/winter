import types
from typing import Mapping
from typing import Tuple


class InvalidMediaTypeException(Exception):
    def __init__(self, media_type: str, message: str):
        super().__init__(f'{message}: {media_type}')
        self.media_type = media_type
        self.message = message


class MediaType:
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

    def __init__(self, media_type_str: str):
        self._type_ = '*'
        self._subtype = '*'
        self._parameters: Mapping[str, str] = {}
        self._type, self._subtype, self._parameters = self.parse(media_type_str)

    @property
    def type(self) -> str:
        return self._type

    @property
    def subtype(self) -> str:
        return self._subtype

    @property
    def parameters(self) -> Mapping[str, str]:
        return self._parameters

    @classmethod
    def parse(cls, media_type: str) -> Tuple[str, str, Mapping[str, str]]:
        media_type = media_type.strip()
        if not media_type:
            raise InvalidMediaTypeException(media_type, 'Media type must not be empty')

        full_type, *parameters_parts = media_type.split(';')
        parameters = cls._parse_parameters(media_type, parameters_parts)
        type_, subtype = cls._parse_full_type(media_type, full_type)
        return type_, subtype, parameters

    @classmethod
    def _parse_parameters(cls, media_type_str, parts) -> Mapping[str, str]:
        parameters = {}
        for param_str in parts:
            key_value = param_str.strip().split('=')
            if len(key_value) != 2:
                raise InvalidMediaTypeException(media_type_str, 'Invalid media type parameter list')
            key, value = (item.strip() for item in key_value)
            parameters[key] = value
        return types.MappingProxyType(parameters)

    @classmethod
    def _parse_full_type(cls, media_type_str, full_type) -> Tuple[str, str]:
        type_, separator, subtype = full_type.partition('/')

        if type_ == '*' and separator == '':
            subtype = '*'
            separator = '/'

        type_ = type_.strip()
        subtype = subtype.strip()

        cls._check(media_type_str, type_, separator, subtype)
        return type_, subtype

    @classmethod
    def _check(cls, media_type_str, type_, separator, subtype) -> None:
        cls._check_for_empty(media_type_str, type_, separator, subtype)
        if subtype.count('/'):
            raise InvalidMediaTypeException(media_type_str, 'Invalid media type format')
        if type_ == '*' and subtype != '*':
            raise InvalidMediaTypeException(media_type_str, 'Wildcard is allowed only in */* (all media types)')

    @classmethod
    def _check_for_empty(self, media_type_str, type_, separator, subtype) -> None:
        if not separator:
            raise InvalidMediaTypeException(media_type_str, 'Media type must contain "/"')
        if not type_:
            raise InvalidMediaTypeException(media_type_str, 'Empty type is specified')
        if not subtype:
            raise InvalidMediaTypeException(media_type_str, 'Empty subtype is specified')

    def __eq__(self, other) -> bool:
        if not isinstance(other, MediaType):
            return False
        return other.type == self.type and other.subtype == self.subtype and other.parameters == self.parameters

    def __hash__(self) -> int:
        return hash((self._type, self._subtype, tuple(self._parameters.items())))

    def __str__(self) -> str:
        full_type = f'{self.type}/{self.subtype}'
        if self.parameters:
            parameters_strings = [f'{k}={v}' for k, v in self.parameters.items()]
            return full_type + '; ' + '; '.join(parameters_strings)
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
