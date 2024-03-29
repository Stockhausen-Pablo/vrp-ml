from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    usage_license = f.read()

setup(
    name='vrp-rl',
    version='0.1.0',
    description='Reinforcement Learning by using a MDP/REINFORCE to solve CVRP',
    long_description=readme,
    author='Pablo Stockhausen',
    author_email='stockhausen017@gmail.com',
    url='https://github.com/Stockhausen-Pablo/vrp-rl',
    license=usage_license,
    packages=find_packages(exclude=('tests', 'docs'))
)