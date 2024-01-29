from setuptools import setup, find_packages

a = setup(
    name="datahinge-cli",
    version="1.0.0",
    author="Sudo-Ivan",
    author_email="contact@ivanryan.slmail.me",
    description="A command-line interface for my awesome Python project",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "datahinge-cli=datahinge_cli.__main__:main"
        ]
    },
    install_requires=[
        "prompt_toolkit>=3.0.36",
        "pygments>=2.7.0",
        "GitPython>=3.1.31",
        "requests>=2.28.2",
    ]
)