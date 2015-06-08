from collections import defaultdict
from django.core.urlresolvers import resolve, reverse


class MenuRegistry(object):
    def __init__(self):
        self.menus = defaultdict(list)

    def __getitem__(self, menu):
        return self.menus[menu]


menu_registry = MenuRegistry()


class Menu(object):
    def __init__(self, items):
        self.items = items

    def calculate(self, context):
        resolved = resolve(context['request'].path_info)
        if resolved.namespace:
            current = '%s:%s' % (resolved.namespace, resolved.url_name)
        else:
            current = resolved.url_name
        for item in self.items:
            yield {'url': reverse(item.url), 'name': item.name, 'visible': item.predicate(context),
                   'active': current == item.url}


class MenuItem(object):
    def __init__(self, url, name, weight=10, predicate=lambda _: True):
        self.url = url
        self.name = name
        self.weight = weight
        self.predicate = predicate
