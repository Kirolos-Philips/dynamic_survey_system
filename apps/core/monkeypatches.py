def apply_monkeypatches():
    import collections
    import collections.abc

    from django.template import defaultfilters

    # Monkeypatch for django-jet compatibility with Python 3.10+
    if not hasattr(collections, "MutableSet"):
        collections.MutableSet = collections.abc.MutableSet

    if not hasattr(collections, "MutableMapping"):
        collections.MutableMapping = collections.abc.MutableMapping

    if not hasattr(collections, "Iterable"):
        collections.Iterable = collections.abc.Iterable

    # Monkeypatch length_is filter for Django 5.1+ compatibility
    if not hasattr(defaultfilters, "_length_is_patched"):

        def length_is(value, arg):
            try:
                return len(value) == int(arg)
            except (ValueError, TypeError):
                return None

        defaultfilters.register.filter("length_is", length_is)
        defaultfilters._length_is_patched = True
