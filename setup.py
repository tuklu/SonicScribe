from setuptools import setup, find_packages

# Ensure UTF-8 encoding when reading files
import codecs
import os

def read_file(filename):
    with codecs.open(os.path.join(os.path.dirname(__file__), filename), encoding="utf-8") as f:
        return f.read()

setup(
    name="sonicscribe",
    version="1.0.0",
    description="🎙️ SonicScribe - Transcribe & Translate audio/video files using Whisper and GPT models.",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Jisnu Kalita",
    author_email="ssh@tuklu.dev",
    url="https://github.com/tuklu/SonicScribe.git",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
        "moviepy>=1.0.3",
        "python-dotenv>=1.0.0",
        "tenacity>=8.0.0",
        "rich>=13.0.0",
        "pydub>=0.25.1",
        "typing-extensions>=4.0.0"
    ],
    entry_points={
        "console_scripts": [
            "sonicscribe=sonicscribe.main:main",
            "translate-srt=sonicscribe.translate_srt:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)