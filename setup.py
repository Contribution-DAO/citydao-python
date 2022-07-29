import setuptools


with open("requirements.txt", "r") as fp:
    requirements = [
        lib.strip()
        for lib in fp.readlines()
    ]


with open("README.md", "r") as fp:
    long_description = fp.read()


setuptools.setup(
    name="citydao",
    version="0.0.1",
    author="Chompakorn Chaksangchaichot",
    author_email="chompakorn.c@contributiondao.com",
    description="CityDAO utility python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires=">=3.10"
)