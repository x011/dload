from pathlib import Path

from setuptools import find_packages, setup


def read_readme() -> str:
    readme_path = Path(__file__).parent / "README.md"
    return readme_path.read_text(encoding="utf-8")


setup(
    name="dload",
    version="0.7.0",
    description="A multipurpose downloader for Python >= 3.6",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="xTudo",
    author_email="dload@11.to",
    url="https://github.com/x011/dload",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["requests>=2.11.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
