from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import int
from future import standard_library
standard_library.install_aliases()
import re

_reg_loss = re.compile(r'\bIteration\s\d+, loss\s=\s[0-9\.]+\b')
_reg_acc = re.compile(r'accuracy\s=\s[0-9\.]+', flags=re.DOTALL)
_reg_iter = re.compile(r'Iteration\s\d+')


def parse_caffe_train_line(line):
    """Parse a line from Caffe's training output

    Arguments
    ---------
    line : string
        Line to parse from training

    Returns
    -------
    training_event : dictionary
        A (possibly incomplete) dict with the parsed information
    """
    line = line.replace('\n', '')
    training_event = {}

    loss_match = re.findall(_reg_loss, line)
    acc_match = re.findall(_reg_acc, line)
    iteration_match = re.findall(_reg_iter, line)
    if iteration_match:
        training_event['iteration'] = int(iteration_match[0].replace('Iteration ', ''))
    if loss_match:
        iteration_str, loss_str = loss_match[0].split(',')
        training_event['loss'] = float(loss_str.replace('loss = ', ''))
    elif acc_match:
        training_event['accuracy'] = float(acc_match[0].replace('accuracy = ', ''))
    return training_event
