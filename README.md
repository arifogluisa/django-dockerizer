[![](https://img.shields.io/pypi/pyversions/django-colorfield.svg?color=3776AB&logo=python&logoColor=white)](https://www.python.org/)
[![](https://img.shields.io/pypi/djversions/django-colorfield?color=0C4B33&logo=django&logoColor=white&label=django)](https://www.djangoproject.com/)

[![](https://img.shields.io/pypi/v/django-dockerizer.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-dockerizer/)
[![Downloads](https://static.pepy.tech/badge/django-dockerizer)](https://pepy.tech/project/django-dockerizer)
[![](https://img.shields.io/github/stars/arifogluisa/django-dockerizer?logo=github)](https://github.com/arifogluisa/django-dockerizer/stargazers)
[![](https://img.shields.io/pypi/l/django-dockerizer.svg?color=blue)](https://github.com/arifogluisa/django-dockerizer/blob/master/LICENSE)

[![](https://img.shields.io/codacy/grade/194566618f424a819ce43450ea0af081?logo=codacy)](https://app.codacy.com/gh/arifogluisa/django-dockerizer)
[![](https://img.shields.io/codeclimate/maintainability/arifogluisa/django-dockerizer?logo=code-climate)](https://codeclimate.com/github/arifogluisa/django-dockerizer/)
[![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# django-dockerizer
A package used to dockerize and make ready Django projects to deploy.


## Installation
-   Run `pip install django-dockerizer`


## Usage

### Without celery
-   Run `dockerize` command in project's base directory (in the same directory with manage.py file)

### With celery
-   Run `dockerize --celery` command in project's base directory (in the same directory with manage.py file)

### Requirements
-   It creates `requirements.txt` files in `bin/dev` and `bin/prod` folders. And all packages which installed in virtual environment(if there is an activated one) or in the system, will be written in `requirements.txt` files. Just be sure there are Django, psycopg2-binary, celery, django_celery_results, django_celery_beat in INSTALLED_APPS in settings.py

### Database
-   It configures docker-compose for Postgresql database, so be sure your DATABASE configuration in settings.py is okay for Postgresql database with credentials in .env file

## Credits
Originally developed by [Isa Arifoglu](https://github.com/arifogluisa)


## License
Released under [MIT License](LICENSE).


## Supporting

- :star: Star this project on [GitHub](https://github.com/arifogluisa/django-dockerizer)
- :octocat: Follow me on [GitHub](https://github.com/arifogluisa)
- :blue_heart: Follow me on [Twitter](https://twitter.com/arifogluisa)
