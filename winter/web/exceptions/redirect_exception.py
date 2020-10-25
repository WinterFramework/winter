class RedirectException(Exception):
    def __init__(self, redirect_to: str):
        super().__init__()
        self.redirect_to = redirect_to
