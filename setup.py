from setuptools import setup

with open("README", 'r') as f:
    long_description = f.read()

# https://github.com/navdeep-G/setup.py
setup(name='uneats',
      version='0.1',
      description='provides the means to describe physical quantities in terms of values and units',
      long_description=long_description,
      url='https://github.com/TGFKA/units',
      author='Philip Geißler, Kamal Abdellatif, Tim Gerlach',
      license='MIT',
      packages=['uneats'],
      install_requires=['numpy'],
      include_package_data=True,
      zip_safe=False)
