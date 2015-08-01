Mri
========
[![Build Status](https://travis-ci.org/Mri-monitoring/Mri-app.svg?branch=master)](https://travis-ci.org/Mri-monitoring/Mri-app)
[![Documentation Status](https://readthedocs.org/projects/mri/badge/?version=latest)](https://readthedocs.org/projects/mri/?badge=latest)

> Neural network monitoring

Mri-app is an application that allows you to monitor training of neural networks remotely via web interface, as well as test many architectures and hyperparameters automatically. For installation and instructions, see [the documentation](http://mri.readthedocs.org/en/latest)

## Dependencies

In its current state, Mri requires:

### [Caffe](http://caffe.berkeleyvision.org/)

Mri currently only works with Caffe. The officially supported version of Caffe is always the latest release, but you can probably get away with older releases easily.

### [Python](https://www.python.org/)

Both Python 2.7 and Python 3 are supported. However, some features will only work in Python 2.7, due to Caffe's Python wrapper support. You will need other packages depending on which features you want to use, see `requirements.txt` for more.
