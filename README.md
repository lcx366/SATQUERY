# Welcome to the SATQUERY package

[![PyPI version shields.io](https://img.shields.io/pypi/v/satcatalogquery.svg)](https://pypi.python.org/pypi/satcatalogquery/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/satcatalogquery.svg)](https://pypi.python.org/pypi/satcatalogquery/) [![PyPI status](https://img.shields.io/pypi/status/satcatalogquery.svg)](https://pypi.python.org/pypi/satcatalogquery/) [![GitHub contributors](https://img.shields.io/github/contributors/lcx366/SATQUERY.svg)](https://GitHub.com/lcx366/SATQUERY/graphs/contributors/) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/lcx366/SATQUERY/graphs/commit-activity) [![GitHub license](https://img.shields.io/github/license/lcx366/SATQUERY.svg)](https://github.com/lcx366/SATQUERY/blob/master/LICENSE) [![Documentation Status](https://readthedocs.org/projects/pystmos/badge/?version=latest)](http://satcatalogquery.readthedocs.io/?badge=latest) [![Build Status](https://travis-ci.org/lcx366/satcatalogquery.svg?branch=master)](https://travis-ci.org/lcx366/satcatalogquery)

This package is an archive of scientific routines for data processing related to the space targets catalogue query. 
Currently, operations on  targets catalogue query include:

1. targets catalogue query on shape info from DISCOS(Database and Information System Characterising Objects in Space) database;
2. targets catalogue query on orbit info from CelesTrak database;
3. targets catalogue query on both shape and orbit from a combined database;

## How to Install

On Linux, macOS and Windows architectures, the binary wheels can be installed using pip by executing one of the following commands:

```
pip install satcatalogquery
pip install satcatalogquery --upgrade # to upgrade a pre-existing installation
```

## How to use

### Targets catalogue query from DISCOS

Query by NORAD_ID, where type of NORAD_ID can be int/str, list of int/str,  or a text file named satno.txt in the following format:

```
# satno
52132
51454
37637
26758
44691
```

```python
>>> from satcatalogquery import discos_query
>>> satcatlog = discos_query(NORAD_ID=[52132,51454,37637,26758,44691])
>>> # satcatog = discos_query(NORAD_ID='satno.txt')
>>> satcatlog.df # output pandas dataframe
>>> satcatlog.save() # save dataframe to .csv file
```

Query by mutiple options at the same time, such as COSPAR_ID, MASS, SHAPE, RCSAvg, etc.

```python
>>> from satcatalogquery import discos_query
>>> satcatlog = discos_query(SHAPE=['Box','Pan'],RCSAvg=[0.5,100],DECAYED=False)
```

#### Targets catalogue query from CelesTrak

```python
>>> from satcatalogquery import celestrak_query
>>> satcatlog = celestrak_query(MEAN_ALT=[300,2000],ECC=[0.01,0.1],PAYLOAD=False)
```

### Targets catalogue query from combined database

```python
>>> from satcatalogquery import targets_query
>>> satcatlog = targets_query(DECAYED=False,RCSAvg=[0.25,1e4],MEAN_ALT=[250,2000],TLE_STATUS=True,sort='RCSAvg')
```

### Create object `SatCatlog` from a loacl .csv file

```python
>>> from satcatalogquery import SatCatlog
>>> satcatlog = SatCatlog.from_csv('filename.csv')
```

### Statistics

```python
>>> satcatlog.hist1d('RCSAvg')
>>> satcatlog.hist1d(['StdMag','LAUNCH_DATE'])
>>> satcatlog.hist2d('MEAN_ALT','INCLINATION')
>>> satcatlog.pie('LAUNCH_SITE',cutoff=100)
```

<p align="middle">
  <img src="readme_figs/RCSAvg.png" width="500" />
</p>

<p align="middle">
  <img src="readme_figs/StdMag_LAUNCH_DATE.png" width="500" />
</p>

<p align="middle">
  <img src="readme_figs/MEAN_ALT-INCLINATION.png" width="500" />
</p>

<p align="middle">
  <img src="readme_figs/LAUNCH_SITE.png" width="500" />
</p>

### Download TLE from results of targets catalogue query

```python
>>> tle_path = satcatlog.get_tle()
```

## Change log

- **0.2.1 ??? Jan 4, 2023**
  
  - Add method `from_csv` and `pie` to class SatCatlog
  
  - Add statistics figures to README.md

- **0.1.1 ??? Jan 2,  2023**
  
  - The ***satcatalogquery*** package was released.

## Reference

- [DISCOSweb](https://discosweb.esoc.esa.int)
- [CelesTrak](http://www.celestrak.com) and [SATCAT Format Documentation](https://celestrak.org/satcat/satcat-format.php)
- [Space-Track](https://www.space-track.org/auth/login)