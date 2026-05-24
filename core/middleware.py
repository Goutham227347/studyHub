class RecentlyViewedMiddleware:
    """Attach session key for anonymous recently viewed tracking."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.create()
        request.studyhub_session_key = request.session.session_key
        return self.get_response(request)
