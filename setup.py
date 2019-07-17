from distutils.core import setup
from pip.req import parse_requirements

# Loading requirements
install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='seal_regression',
    version='0.0',
    author='Valentyn Melnychuk, Diana Devletshyna',
    author_email='v.melnychuk@campus.lmu.de, ',
    description='Implementation of Linear Regression on encrypted data with PySEAL',
    install_requires=reqs,
    packages=['seal_regression'],
    scripts=['install_pyseal.sh'],
)
