Mri
========

> Neural network monitoring

Mri is a set of applications designed to allow you to easily monitor network training and automatically test architectures and hyperparameters. For now, Mri is designed to work with [Caffe](http://caffe.berkeleyvision.org/), but keep an eye out for other backends in the future.

This project relies on an open-source fork of [Reportr](http://www.reportr.io/) for browser based monitoring.

## Installing

To install, clone the git repository and enter the `Mri` directory. 

```
$ git clone REPOLOCATIONHERE
$ cd Mri
$ cp config.Template config.txt
```

Make appropriate edits to the config file, then install and run.

```
$ cd ..
$ python setup.py install
$ python Mri/MriApp.py Mri/config.txt
```

## Architecture 

In general Mri is designed for modularity. There are three central components to Mri:

* Processes - A process is the actual training process. While it doesn't need to be a literal CPU process, in the case of Caffe it is.
* Dispatch - Specifies how and where Mri will send training/testing information. Currently there is a barebones Matplotlib dispatch, and a more complete MriServer dispatch.
* Retrieve - Because Mri can run multiple jobs in queue, the retriever specifies how to fetch the next job. Currently there is only the option to use a local file.

## Dependencies

In its current state, Mri requires:

### [Caffe](http://caffe.berkeleyvision.org/)

Mri currently only works with Caffe. The officially supported version of Caffe is always the latest release, but you can probably get away with older releases easily.

### [Python](https://www.python.org/)

Both Python 2.7 and Python 3 are supported. However, some features will only work in Python 2.7, due to Caffe's Python wrapper support. You will need other packages depending on which features you want to use, see `requirements.txt` for more.

## Configuration

The Mri configuration file is a plain-text file that contains all the required configuration settings. See the configuration template for an example. Note that not all modules are required, i.e. if you only plan to use the matplotlib-dispatch option, you do not need any other dispatch configuration settings.
