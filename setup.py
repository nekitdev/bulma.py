import re

from pathlib import Path
from setuptools import setup  # type: ignore

root = Path(__file__).parent

requirements = (root / "requirements.txt").read_text("utf-8").strip().splitlines()

text = (root / "bulma" / "__init__.py").read_text("utf-8")

version_regex = re.compile(r"^__version__\s*=\s*[\"']([^\"']*)[\"']", re.MULTILINE)
version_match = version_regex.search(text)

if version_match is None:
    raise RuntimeError("Failed to find version.")


version = version_match.group(1)

readme = (root / "README.rst").read_text("utf-8")


setup(
    name="bulma.py",
    author="nekitdev",
    author_email="nekitdevofficial@gmail.com",
    url="https://github.com/nekitdev/bulma.py",
    project_urls={
        "Issue tracker": "https://github.com/nekitdev/bulma.py/issues",
    },
    version=version,
    packages=["bulma"],
    license="MIT",
    description="Small Compiler for Bulma and Extensions.",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
)
