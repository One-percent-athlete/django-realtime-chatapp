from django.apps import AppConfig


class ChatuserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatuser'

    def ready(self):
        import chatuser.signals
