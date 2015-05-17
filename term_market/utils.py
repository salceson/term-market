class FakeQuerySet(object):
    def __init__(self, items):
        self.items = items

    def iterator(self):
        for item in self.items:
            yield item