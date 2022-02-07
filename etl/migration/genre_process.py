from etl.config_validation.indexes import Genre
from etl.migration.main_process import UnifiedProcess


class GenreProcess(UnifiedProcess):
    validation_model = Genre
