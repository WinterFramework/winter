from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar

AnnotationType = TypeVar('AnnotationType')


class AnnotationException(Exception):
    pass


class MultipleAnnotationFound(AnnotationException):

    def __init__(self, annotation_type: AnnotationType, count: int):
        self.annotation_type = annotation_type
        self.count = count

    def __str__(self):
        return f'Found more than one annotation for {self.annotation_type}: {self.count}'


class NotFoundAnnotation(AnnotationException):

    def __init__(self, annotation_type: AnnotationType):
        self.annotation_type = annotation_type
        super().__init__(annotation_type)

    def __str__(self):
        return f'Not found annotation for {self.annotation_type}'


class AlreadyAnnotated(AnnotationException):

    def __init__(self, annotation: AnnotationType):
        self.annotation = annotation

    def __str__(self):
        return f'Cannot annotate twice: {type(self.annotation)}'


class Annotations:

    def __init__(self):
        self._data: Dict = {}

    def get(self, annotation_type: AnnotationType) -> List[AnnotationType]:
        return self._data.get(annotation_type, [])

    def get_one_or_none(self, annotation_type: AnnotationType) -> Optional[AnnotationType]:
        annotations = self.get(annotation_type)

        count_annotations = len(annotations)

        if count_annotations > 1:
            raise MultipleAnnotationFound(annotation_type, count_annotations)

        return annotations[0] if annotations else None

    def get_one(self, annotation_type: AnnotationType) -> AnnotationType:
        annotation = self.get_one_or_none(annotation_type)
        if annotation is None:
            raise NotFoundAnnotation(annotation_type)
        return annotation

    def add(self, annotation: AnnotationType, unique=False, single=False):
        annotation_type = annotation.__class__

        if single and annotation_type in self._data:
            raise AlreadyAnnotated(annotation)

        annotations = self._data.setdefault(annotation_type, [])

        if unique and annotation in annotations:
            raise AlreadyAnnotated(annotation)

        annotations.append(annotation)
