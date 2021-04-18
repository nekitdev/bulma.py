from pathlib import Path
import re

from setuptools import setup  # type: ignore

root = Path(__file__).parent

requirements = (root / "requirements.txt").read_text("utf-8").strip().splitlines()

init = (root / "bulma" / "__init__.py").read_text("utf-8")

result = re.search(r"^__version__\s*=\s*[\"']([^\"']*)[\"']", init, re.MULTILINE)

if result is None:
    raise RuntimeError("Failed to find version.")

version = result.group(1)

long_description = (root / "README.rst").read_text("utf-8")


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
    long_description=long_description,
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
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
)
