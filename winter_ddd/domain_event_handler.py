from winter.core import annotate


class DomainEventHandlerAnnotation:
    pass


domain_event_handler = annotate(DomainEventHandlerAnnotation(), single=True)
