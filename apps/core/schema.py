from drf_spectacular.openapi import AutoSchema


class AppGroupingAutoSchema(AutoSchema):
    def get_tags(self):
        """
        Groups endpoints by app name instead of the default 'api' or URL path prefix.
        """
        tags = super().get_tags()

        # Check if we should override the tags. By default spectacular often puts
        # things in 'api' or 'en' based on url path if no tags are provided.
        if not tags or tags == ["api"] or tags == ["en"]:
            try:
                # Resolve the view's module to find which app it belongs to
                module_path = self.view.__class__.__module__

                # We expect apps to be in the 'apps' directory
                if module_path.startswith("apps."):
                    parts = module_path.split(".")
                    if len(parts) > 1:
                        app_name = parts[1]
                        # Humanize the app name: 'surveys' -> 'Surveys'
                        humanized_name = app_name.replace("_", " ").title()
                        return [humanized_name]
            except (AttributeError, IndexError):
                pass

        return tags
