#  https://stackoverflow.com/questions/4292398/django-define-a-form-differently-when-in-testing-mode
# решение проблем с требованием required CaptchaField в тестах
from captcha.fields import CaptchaField
CaptchaField.clean = lambda x, y: y
