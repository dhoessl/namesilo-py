from setuptools import setup, find_packages

setup(
    name="namesilo-py",
    version="0.0.4",
    description=(
        "module to add, delete and modify DNS Records on Namesilo.com"
    ),
    url="https://github.com/dhoessl/namesilo-py.git",
    author="Dominic Hößl",
    author_email="dhoessl@dhoessl.de",
    license="GPL-v3",
    packages=find_packages(exclude=["docs", "docs.*"]),
    package_data={},
    include_package_data=True,
    install_requires=["loguru", "requests", "pyyaml"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ]
)
