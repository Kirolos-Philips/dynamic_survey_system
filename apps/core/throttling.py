from rest_framework.throttling import ScopedRateThrottle


class ActionBasedThrottle(ScopedRateThrottle):
    """
    Custom throttle class that allows different rates based on the action (for ViewSets)
    or the method (for APIViews).
    """

    def allow_request(self, request, view):
        # 1. Get the unified throttle map from the view
        throttle_map = getattr(view, "throttle_map", {})

        # 2. Try to find a match:
        # Priority 1: Current Action (for ViewSets like 'create', 'list')
        # Priority 2: Current HTTP Method (for APIViews like 'get', 'post')
        action = getattr(view, "action", None)
        method = request.method.lower()

        value = throttle_map.get(action) or throttle_map.get(method)

        if not value:
            # Fallback to default behavior if no mapping is provided
            return super().allow_request(request, view)

        # 3. Determine if it's a direct rate string or a pre-configured scope
        if "/" in value:
            self.rate = value
            self.scope = value  # Use rate as scope for unique cache keys
        else:
            self.scope = value
            self.rate = self.get_rate()

        if not self.rate:
            return True

        self.num_requests, self.duration = self.parse_rate(self.rate)

        return super().allow_request(request, view)
