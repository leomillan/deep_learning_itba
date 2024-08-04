from app.services.configuration.configuration_service import ConfigurationManager
from app.services.database.database_service import DatabaseService
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    """Container to inject all services needed in the application"""

    config = providers.Configuration()
    config.from_dict(ConfigurationManager.init_config())

    sql_db = providers.Singleton(DatabaseService, config=config.sql)
