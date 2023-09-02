# create setup file

from setuptools import setup, find_packages

setup(
    name='pptx-explainer',
    version='0.1.0',
    author='Gal Malka',
    author_email='galmalka122@gmail.com',
    description='A package to generate explanations for PowerPoint presentations',
    url='https://github.com/Scaleup-Excellenteam/final-exercise-galmalka122',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-dotenv',
        'python-pptx',
        'openai',
        'Flask'],
    entry_points={
        'console_scripts': [
            'pptx-explainer = pptx_explainer.__main__:main'
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.9',
    ],
)
