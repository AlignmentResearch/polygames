from setuptools import setup

setup(
    name="polygames",
    version="1.0",
    description="A collection of games",
    author="The Polygames authors",
    license="MIT",
    packages=[
        "pypolygames",
        "pytube",
    ],
    package_dir={
        "pypolygames": "pypolygames",
        "pytube": "src/tube/pytube",
    },
    package_data={"pypolygames": ["build/src/polygames*.so"]},
    python_requires=">=3.9",
)
