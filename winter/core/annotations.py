import typing

AnnotationType = typing.TypeVar('AnnotationType')


class AnnotationException(Exception):
    pass


class MultipleAnnotationFound(AnnotationException):

    def __init__(self, annotation_key: typing.Hashable, count: int):
        self.annotation_key = annotation_key
        self.count = count

    def __str__(self):
        return f'Found more than one annotation for {self.annotation_key}: {self.count}'


class NotFoundAnnotation(AnnotationException):

    def __init__(self, annotation_key: typing.Hashable):
        self.annotation_key = annotation_key
        super().__init__(annotation_key)

    def __str__(self):
        return f'Not found annotation for {self.annotation_key}'


class AlreadyAnnotated(AnnotationException):

    def __init__(self, annotation: AnnotationType):
        self.annotation = annotation

    def __str__(self):
        return f'Cannot annotate twice {type(self.annotation)}'


class Annotations:

    def __init__(self):
        self._data: typing.Dict = {}

    def get(self, key: typing.Hashable) -> typing.List[AnnotationType]:
        return self._data.get(key, [])

    def get_one_or_none(self, key: typing.Hashable) -> typing.Optional[AnnotationType]:
        annotations = self.get(key)

        count_annotations = len(annotations)

        if count_annotations > 1:
            raise MultipleAnnotationFound(key, count_annotations)

        return annotations[0] if annotations else None

    def get_one(self, key: typing.Hashable) -> AnnotationType:
        annotation = self.get_one_or_none(key)
        if annotation is None:
            raise NotFoundAnnotation(key)
        return annotation

    def add(self, annotation: AnnotationType, key: typing.Optional[typing.Hashable] = None, unique=False, single=False):
        key = key if key is not None else annotation.__class__

        if single and key in self._data:
            raise AlreadyAnnotated(annotation)

        annotations = self._data.setdefault(key, [])

        if unique and annotation in annotations:
            raise AlreadyAnnotated(annotation)

        annotations.append(annotation)
