from setuptools import setup, find_packages

setup(
    name='abm1559',
    url='https://github.com/barnabemonnot/abm1559',
    author='Barnabé Monnot',
    author_email='barnabe.monnot@ethereum.org',
    packages=find_packages(include=['abm1559', 'abm1559.*']),
    install_requires=['numpy', 'pandas'],
    version='0.0.2',
    license='MIT',
    description='Agent-based simulation environment for EIP 1559',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
)
