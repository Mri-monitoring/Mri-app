"""Mri is a tool for monitoring neural network training in Caffe"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from mriapp.MriCaffe import MriCaffe

import argparse


def main():
    """Entry point for Mri"""
    parser = argparse.ArgumentParser(description='Monitoring tool for Caffe')
    parser.add_argument('config_file')
    arg = parser.parse_args()

    client = MriCaffe(arg.config_file)
    client.start()

if __name__ == "__main__":
    main()
