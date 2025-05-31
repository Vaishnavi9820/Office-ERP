from django.apps import AppConfig


class EmployeeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employee'
    
    def ready(self):
        # Import signals here to avoid AppRegistryNotReady exception
        import employee.signals
