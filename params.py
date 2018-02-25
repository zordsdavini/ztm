class Params:
    singleton = None

    params = {
        'active': False,
        'done': False,
    }

    def __new__(cls, *args, **kwargs):
        if not cls.singleton:
            cls.singleton = object.__new__(Params)
        return cls.singleton

    def update(self, key, value):
        self.params[key] = value

    def get(self, key):
        return self.params[key]
