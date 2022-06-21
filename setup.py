from setuptools import find_packages, setup  # type: ignore

# Library dependencies
INSTALL_REQUIRES = [
    "boto3>=1.16.42",
    "melitk.metrics",
    "melitk.logging",
]

# Development dependencies
DEV_REQUIRES = []

# Testing dependencies
TEST_REQUIRES = [
    "codecov==2.0.15",
    "coverage==4.5.2",
    "pytest==4.0.0",
    "pytest-cov==2.6.0",
    "pytest-mock==1.10.4",
    "requests-mock==1.8.0",
    "moto",
]

# To identify versions follow the scheme defined in PEP-440:
# https://www.python.org/dev/peps/pep-0440/
# (It is similar to Semantic Versioning https://semver.org/, with minor differences)
setup(
    name="sibila",
    version="1.2.4",
    description="Autoforecasting Lib",
    author="BI ML Cross Team",
    author_email="bi-ml-cross@mercadolibre.com",
    url="git@github.com:mercadolibre/python-bi-automl.git",
    packages=find_packages(),
    python_requires=">=3.6",
    setup_requires=["wheel"],
    install_requires=INSTALL_REQUIRES,
    extras_require={"dev": DEV_REQUIRES, "test": TEST_REQUIRES},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development",
    ],
)
