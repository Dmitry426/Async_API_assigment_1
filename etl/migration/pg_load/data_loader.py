import abc


class DataLoader:
    """
    Basic data loader class
    """

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def postgres_producer(self, cursor, query: str, *args, **kwargs):
        pass

    @abc.abstractmethod
    def postgres_enricher(self, cursor, ids: str, *args, **kwargs):
        pass

    @abc.abstractmethod
    def postgres_merger(self, cursor, *args, **kwargs):
        pass
