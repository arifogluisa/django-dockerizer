import os
import random
import string


BASE_DIR = os.getcwd()


def find_django_project_name():
    for root, dirs, files in os.walk(BASE_DIR):
        if "settings.py" in files:
            settings_path = os.path.join(root, "settings.py")
            with open(settings_path, 'r') as file:
                contents = file.read()
                if 'django.contrib' in contents:
                    return os.path.basename(root), root
    raise Exception("Could not find Django project name")


PROJECT_NAME, SETTINGS_DIRECTORY = find_django_project_name()


def generate_password(length=12):
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_env_variable(env_file, variable_name):
    with open(env_file, 'r') as file:
        for line in file:
            if line.startswith(variable_name):
                return line.split('=')[1].strip()
    return None


def generate_or_retrieve_passwords():
    env_file_path = os.path.join(BASE_DIR, 'bin/dev', '.env')

    # Check if .env file exists
    if os.path.exists(env_file_path):
        db_pass = get_env_variable(env_file_path, 'POSTGRES_PASSWORD')
        redis_pass = get_env_variable(env_file_path, 'REDIS_PASSWORD')
        # If for any reason the variables aren't in the .env file, generate new ones
        if not db_pass:
            db_pass = generate_password(65)
        if not redis_pass:
            redis_pass = generate_password(16)
    else:
        db_pass = generate_password(65)
        redis_pass = generate_password(16)

    return db_pass, redis_pass


def create_celery_file(content):
    celery_path = os.path.join(SETTINGS_DIRECTORY, 'celery.py')

    if not os.path.exists(celery_path):
        with open(celery_path, 'w') as file:
            file.write(content)
