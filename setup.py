"""
Setup script for wlibrary
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        ]
else:
    requirements = [
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "openpyxl>=3.1.0",
    ]

setup(
    name="wlibrary",
    version="1.1.0",
    author="Sidorov Denis",
    author_email="sidorovdenys9@gmail.com",
    description="Universal Excel file processing library for intelligent data import, cleaning, analysis, and export",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zonda001/wlibrary",
    project_urls={
        "Bug Tracker": "https://github.com/Zonda001/wlibrary/issues",
        "Source Code": "https://github.com/Zonda001/wlibrary",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    keywords=["excel", "data-processing", "data-cleaning", "pandas", "etl"],
    license="MIT",
)