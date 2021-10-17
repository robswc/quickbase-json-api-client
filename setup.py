from setuptools import find_packages, setup
setup(
    name='quickbase-json',
    packages=find_packages(include=['quickbase_json']),
    version='0.1.0',
    description='Quickbase JSON API wrapper for python',
    author='Robert Carroll',
    license='MIT',
    install_requires=['requests=>2.24.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)