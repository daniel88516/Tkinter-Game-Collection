class MyEvent:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def unsubscribe(self, callback):
        self._subscribers.remove(callback)

    def emit(self, *args, **kwargs):
        for callback in self._subscribers:
            callback(*args, **kwargs)
