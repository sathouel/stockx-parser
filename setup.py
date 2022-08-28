import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stockx-parser",
    version="0.0.6",
    author="Steven Athouel",
    author_email="sathouel@gmail.com",
    description="A simple parser for stockx plateform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sathouel/stockx-parser.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)