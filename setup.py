from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="django_dockerizer",
    version="0.3.0",
    description="Dockerize and make ready to deploy Django projects",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arifogluisa/django-dockerizer",
    author="Isa Arifoglu",
    author_email="arifogluisa@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['dockerize=django_dockerizer.dockerizer:dockerize'],
    },
    python_requires=">=3.8",
)
