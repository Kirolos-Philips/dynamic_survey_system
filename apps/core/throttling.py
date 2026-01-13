from rest_framework.throttling import ScopedRateThrottle


class ActionBasedThrottle(ScopedRateThrottle):
    """
    Custom throttle class that allows different rates based on the action (for ViewSets)
    or the method (for APIViews).
    """

    def allow_request(self, request, view):
        # 1. Action-based throttling (for ViewSets)
        if hasattr(view, "action") and view.action:
            action_scopes = getattr(view, "throttle_action_scopes", {})
            action_scope = action_scopes.get(view.action)
            if action_scope:
                self.scope = action_scope

        # 2. Method-based throttling (for APIViews or fallback)
        method_scopes = getattr(view, "throttle_method_scopes", {})
        method_scope = method_scopes.get(request.method.lower())
        if method_scope:
            self.scope = method_scope

        # Re-initialize rate based on the dynamically set scope
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

        return super().allow_request(request, view)
