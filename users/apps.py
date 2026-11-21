from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        try:
            import oracle_sync
            oracle_sync.register_oracle_sync_signals()
        except Exception:
            pass
