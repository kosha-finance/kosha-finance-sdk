"""Setup configuration for Kosha Python Client SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kosha-finance-client",
    version="1.0.0",
    author="Kosha Finance Dev Team",
    author_email="opensource@kosha.finance",
    description="Python client SDK for Kosha Finance Reconciliation API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kosha-finance/kosha-finance-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "csv": [
            "pandas>=1.5.0",
        ],
    },
)
