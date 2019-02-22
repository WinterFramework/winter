import typing

AnnotationType = typing.TypeVar('AnnotationType')


class AnnotationException(Exception):

    def __init__(self, value_type: AnnotationType):
        self.annotation_type = value_type
        super().__init__(value_type)


class MultipleAnnotationFound(AnnotationException):

    def __init__(self, value_type: AnnotationType, count: int):
        super().__init__(value_type)
        self.count = count

    def __str__(self):
        return f'Found more than one annotation for {self.annotation_type}: {self.count}'


class NotFoundAnnotation(AnnotationException):

    def __str__(self):
        return f'Not found annotation for {self.annotation_type}'


class Annotations:

    def __init__(self):
        self._data: typing.Dict = {}

    def get(self, annotation_type: typing.Type[AnnotationType]) -> typing.List[AnnotationType]:
        return self._data.get(annotation_type, [])

    def get_one(self, annotation_type: typing.Type[AnnotationType]) -> AnnotationType:
        values = self.get(annotation_type)

        count_values = len(values)

        if not count_values:
            raise NotFoundAnnotation(annotation_type)

        if count_values > 1:
            raise MultipleAnnotationFound(annotation_type, count_values)

        value = values[0]
        return value

    def add(self, annotation: AnnotationType):
        values = self._data.setdefault(annotation.__class__, [])
        values.append(annotation)
