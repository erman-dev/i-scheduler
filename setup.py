from setuptools import setup, find_packages

setup(
    name="inmanta-scheduler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "inmanta-scheduler = scheduler.runner:main",
        ],
    },
)
