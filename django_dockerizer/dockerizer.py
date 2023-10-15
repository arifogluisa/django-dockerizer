import argparse
import os
import subprocess

from .contents import (
    CELERY,
    DEV_ENV,
    DEV_ENV_WITH_CELERY,
    DOCKER_COMPOSE_DEV,
    DOCKER_COMPOSE_PROD,
    DOCKER_COMPOSE_WITH_CELERY_DEV,
    DOCKER_COMPOSE_WITH_CELERY_PROD,
    DOCKERFILE_DEV,
    DOCKERFILE_PROD,
    ENV_TYPES,
    NGINX_CONF,
    PROD_ENV,
    PROD_ENV_WITH_CELERY,
    REDIS_DOCKERFILE,
    SINGLE_FILES,
)
from .utils import BASE_DIR, create_celery_file


def parse_arguments():
    parser = argparse.ArgumentParser(description="Django Dockerizer Tool")
    parser.add_argument(
        "--celery", help="Include Celery configurations", action="store_true"
    )
    # parser.add_argument("--redis", help="Include Redis configurations", action="store_true")

    return parser.parse_args()


args = parse_arguments()


def create_directory_structure():
    os.makedirs(os.path.join(BASE_DIR, "bin/dev"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "bin/prod"), exist_ok=True)


def generate_docker_files(env_type):
    content = DOCKERFILE_DEV if env_type == "dev" else DOCKERFILE_PROD
    with open(os.path.join(BASE_DIR, "bin", env_type, "Dockerfile"), "w") as file:
        file.write(content)
    if args.celery and env_type == "prod":
        with open(
            os.path.join(BASE_DIR, "bin", env_type, "redis.dockerfile"), "w"
        ) as file:
            file.write(REDIS_DOCKERFILE)


def generate_single_files():
    """
    Generating uwsgi.ini, mime.types and nginx.conf files
    """
    for file_name, content in SINGLE_FILES:
        with open(os.path.join(BASE_DIR, "bin", "prod", file_name), "w") as file:
            file.write(content)
    with open(os.path.join(BASE_DIR, "bin", "nginx.conf"), "w") as file:
        file.write(NGINX_CONF)


def generate_env_files(env_type):
    if args.celery:
        content = DEV_ENV_WITH_CELERY if env_type == "dev" else PROD_ENV_WITH_CELERY
    else:
        content = DEV_ENV if env_type == "dev" else PROD_ENV
    with open(os.path.join(BASE_DIR, "bin", env_type, ".env"), "w") as file:
        file.write(content)


def generate_docker_compose_files(env_type):
    if args.celery:
        content = (
            DOCKER_COMPOSE_WITH_CELERY_DEV
            if env_type == "dev"
            else DOCKER_COMPOSE_WITH_CELERY_PROD
        )
    else:
        content = DOCKER_COMPOSE_DEV if env_type == "dev" else DOCKER_COMPOSE_PROD
    with open(
        os.path.join(BASE_DIR, "bin", env_type, "docker-compose.yml"), "w"
    ) as file:
        file.write(content)


def generate_requirements_files(env_type):
    req_path = os.path.join(BASE_DIR, "bin", env_type, "requirements.txt")
    with open(req_path, "w") as file:
        # Run pip freeze and capture the output
        pip_freeze_output = subprocess.check_output(
            ["pip", "freeze"], universal_newlines=True
        )
        file.write(pip_freeze_output)

        # If it's the prod environment, add uwsgi
        if env_type == "prod":
            file.write("uWSGI\n")


def dockerize():
    create_directory_structure()
    generate_single_files()

    if args.celery:
        create_celery_file(CELERY)

    for env_type in ENV_TYPES:
        generate_docker_files(env_type)
        generate_docker_compose_files(env_type)
        generate_env_files(env_type)
        generate_requirements_files(env_type)


if __name__ == "__main__":
    dockerize()
