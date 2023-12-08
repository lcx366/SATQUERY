from setuptools import setup,find_packages 

setup(
    name='satcatalogquery',
    version='0.2.4',
    description='A package for querying orbital and geometric information of spatial objects',
    author='Chunxiao Li',
    author_email='lcx366@126.com',
    url='https://github.com/lcx366/SATQUERY',
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'rb').read().decode('utf-8'),
    keywords = ['DISCOS','CelesTrak','SpaceTrack','Space Debris'],
    python_requires = '>=3.10',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        ],
    packages = find_packages(),
    include_package_data=True,
    install_requires=[
        'spacetrack',
        'numpy>=1.21.2',
        'matplotlib',
        'pandas',
        'wget',
        'colorama',
        ],
)
