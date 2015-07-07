Mri
========

> Neural network monitoring

Mri is a set of applications designed to allow you to easily monitor network training and automatically test architectures and hyperparameters. For now, Mri is designed to work with [Caffe](http://caffe.berkeleyvision.org/) as well as Python applications such as [Theano](http://deeplearning.net/software/theano/). Keep an eye out for other backends in the future.

This project relies on an open-source fork of [Reportr](http://www.reportr.io/) for browser based monitoring.

## Installing

To install, clone the git repository and enter the `Mri` directory. 

```
$ git clone REPOLOCATIONHERE Mri-client
$ cd Mri-client/Mri
$ cp config.Template config.txt
$ cd .. 
```

Optional: create a virtual environment to house the installation.

```
$ mkvirtualenv -p /usr/bin/python2.7 Mri
$ workon Mri
```

Install appropriate requirements to Python and install the Mri library
```
$ pip install -r requirements.txt
$ python setup.py install
```

## Caffe Wrapper
If you are using the Caffe bindings, make appropriate edits to the config file, then install and run.

```
$ python Mri/MriApp.py Mri/config.txt
```

## Python Library
If you are using Mri-client as a Python library to interface with Mri-server, simply import the required modules into your project. See `examples/python_bindings` for example Python code.

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

## Hyperparameter Testing
Included in the `script` directory is a python script that makes it easy to test many hyperparameters in Caffe.

To use, first copy the configuration example to `config` and add your own values. The model and solver templates should simply replace any fields to be replaced by `%{field-name}%`. For example, you may have the following excerpt in your `solver.protobuf` file:

```
# The base learning rate, momentum and the weight decay of the network.
base_lr: %{base_lr}%
momentum: 0.9
weight_decay: %{weight_decay}%
# The learning rate policy
lr_policy: "step"
```

Then, create the hyperparameter file:

```
base_lr: 1e-5, 1e-6, 1e-7
weight_decay: 0.2, 0.1, 0.01
```

The field names can be in either the model or solver, just use unique names

To run script:

```
python generate_tasks random -n 5       # Generates 5 random tasks sampled from the hyperparameter distribution
python generate_tasks grid              # Generate tasks for all possible hyperparameter values
```
