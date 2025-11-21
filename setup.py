"""
Setup script for STTF package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path(__file__).parent / "README.md"
long_description = readme.read_text() if readme.exists() else ""

setup(
    name="sttf",
    version="1.0.0",
    author="STTF Contributors",
    description="SAT Transformation Trace Format - A universal standard for recording SAT CNF transformations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sttf",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "dev": ["pytest", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "sttf-validate=sttf_validate:main",
            "sttf-generate=sttf_generate:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
