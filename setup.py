from setuptools import setup, find_packages

setup(
    name='pymulator',
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'progress',
    ],
    entry_points={
        'console_scripts': [
            'pymulator = pymulator.cmdline:main'
        ]
    },
    author="Giovanni Luca Ciampaglia",
    author_email="glciampagl@gmail.com",
    description="Reproducible simulation for lazy Python programmers",
    license="GPLv3",
    keywords="simulation",
    url="http://github.com/glciampaglia/pymulator"
)
