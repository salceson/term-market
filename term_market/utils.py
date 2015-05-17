def instance_as_queryset(instance):
    return type(instance).objects.filter(pk=instance.pk)