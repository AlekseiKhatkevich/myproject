from functools import wraps


def skip_signal():
    """
    Signal doesnt work when instance has 'skip_signal' = True attribute, to avoid recursion in
    pre_save and post_save.
    Example:

        @receiver(post_save, sender=Product)
        @skip_signal()
        def update_vector(sender, instance, **kwargs):
            instance.textsearchable_index_col = SearchVector('description', config=instance.lang)
            instance.skip_signal = True
            instance.save(update_fields=['textsearchable_index_col', ])

    Will not trigger signal.
    """
    def _skip_signal(signal_func):
        @wraps(signal_func)
        def _decorator(sender, instance, **kwargs):
            if hasattr(instance, 'skip_signal'):
                del instance.skip_signal
                return None
            return signal_func(sender, instance, **kwargs)
        return _decorator
    return _skip_signal
