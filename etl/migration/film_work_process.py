from .main_process import UnifiedProcess
from ..config_validation.indexes import FilmWork


class FilmWorkProcess(UnifiedProcess):
    validation_model = FilmWork
