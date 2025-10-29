"""Setup script for blender-synth."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="blender-synth",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="BlenderProc-based synthetic dataset generator for archaeological artifacts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/blender-synth",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "blenderproc>=2.7.0",
        "numpy>=1.24.0",
        "opencv-python>=4.7.0",
        "Pillow>=9.5.0",
        "PyYAML>=6.0",
        "tqdm>=4.65.0",
        "pydantic>=2.0.0",
        "scipy>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "isort>=5.12.0",
            "mypy>=1.3.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "blender-synth=blender_synth.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "blender_synth": ["py.typed"],
    },
)
