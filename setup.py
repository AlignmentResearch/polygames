from setuptools import setup

setup(
    name="polygames",
    version="1.0",
    description="A collection of games",
    author="The Polygames authors",
    license="MIT",
    packages=["pypolygames"],
    package_data={"pypolygames": ["build/src/polygames*.so"]},
    python_requires=">=3.9",
)
