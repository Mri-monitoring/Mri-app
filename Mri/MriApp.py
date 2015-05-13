"""Mri is a tool for monitoring neural network training in Caffe"""

from Mri.MriClient import MriClient

import argparse


def main():
    """Entry point for Mri"""
    parser = argparse.ArgumentParser(description='Monitoring tool for Caffe')
    parser.add_argument('config_file')
    arg = parser.parse_args()

    client = MriClient(arg.config_file)
    client.start()

if __name__ == "__main__":
    main()
