from django.apps import AppConfig


class EconomicSimulatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'economic_simulator'

    def ready(self):
        from .utility import start_up
        start_up.Start()