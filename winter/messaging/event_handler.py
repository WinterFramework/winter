from winter.components import annotate


class EventHandlerAnnotation:
    pass


annotation = EventHandlerAnnotation()
event_handler = annotate(annotation, single=True)
