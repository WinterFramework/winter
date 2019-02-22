import typing

ValueType = typing.TypeVar('ValueType')


class AnnotationException(Exception):

    def __init__(self, value_type: ValueType):
        self.value_type = value_type
        super().__init__(value_type)


class MultipleAnnotationFound(AnnotationException):

    def __init__(self, value_type: ValueType, count: int):
        super().__init__(value_type)
        self.count = count

    def __str__(self):
        return f'Found more than one annotation for {self.value_type}: {self.count}'


class NotFoundAnnotation(AnnotationException):

    def __str__(self):
        return f'Not found annotation for {self.value_type}'


class Annotations:

    def __init__(self):
        self._data: typing.Dict = {}

    def get(self, value_type: typing.Type[ValueType]) -> typing.List[ValueType]:
        return self._data.get(value_type, [])

    def get_one(self, value_type: typing.Type[ValueType]) -> ValueType:
        values = self.get(value_type)

        count_values = len(values)

        if not count_values:
            raise NotFoundAnnotation(value_type)

        if count_values > 1:
            raise MultipleAnnotationFound(value_type, count_values)

        value = values[0]
        return value

    def add(self, value: ValueType):
        values = self._data.setdefault(value.__class__, [])
        values.append(value)
