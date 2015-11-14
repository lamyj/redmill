import ez_setup
ez_setup.use_setuptools()

from setuptools import find_packages, setup

setup(
    name="Redmill", version="0.3.0",
    author="Julien Lamy", author_email="julien+redmill@seasofcheese.net",
    url="https://github.com/lamyj/redmill",
    description="A web-based picture manager",
    long_description=(
        "Redmill is a web-based picture manager geared toward web sites that "
        "regularly publish images. With both a web-based interface and a "
        "REST API, users can easily set keywords and create derivatives "
        "(e.g. thumbnails or crops) and embed them in the web sites."),
    license="AGPL",

    install_requires=[
        "Flask >= 0.10.1",
        "itsdangerous >= 0.24",
        "SQLAlchemy >= 0.9.8",
        "Unidecode >= 0.04.9",
    ],
    tests_require=["BeautifulSoup4 >= 4.3.2"],
    test_suite = "tests.models",

    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"redmill": ["static/*", "templates/*"]},
)
