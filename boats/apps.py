from django.apps import AppConfig


class BoatsConfig(AppConfig):
    name = 'boats'

    def ready(self):
        import boats.signals



    #  https://stackoverflow.com/questions/7115097/the-right-place-to-keep-my-signals-py-file-in-a-django-project/21612050#21612050


