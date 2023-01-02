from setuptools import setup,find_packages 

setup(
    name='satcatalogquery',
    version='0.1.0',
    description='A package to handle the space targets catalogue query',
    author='Chunxiao Li',
    author_email='lcx366@126.com',
    url='https://github.com/lcx366/SATQUERY',
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'rb').read().decode('utf-8'),
    keywords = ['DISCOS','CelesTrak'],
    python_requires = '>=3.9',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
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
