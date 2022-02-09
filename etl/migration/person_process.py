from etl.config_validation.indexes import Person
from etl.migration.main_process import UnifiedProcess


class PersonProcess(UnifiedProcess):
    validation_model = Person
