from winter.components import annotate


class DomainEventHandlerAnnotation:
    pass


domain_event_handler = annotate(DomainEventHandlerAnnotation(), single=True)
