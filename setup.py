from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eye_break_app",
    version="0.1.0",
    author="Faisal Fida",
    author_email="arainfaisal826@gmail.com",
    description="An app to remind users to take eye breaks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/faisal-fida/eye_break_app",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Pillow",
        "pystray",
    ],
    entry_points={
        "console_scripts": [
            "eye_break_app=eye_break_app.app:main",
        ],
    },
    include_package_data=True,
)
