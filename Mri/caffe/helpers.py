import re

from .TrainingEvent import TrainingEvent

_reg_loss = re.compile(r'\bIteration\s\d+, loss\s=\s[0-9\.]+\b')
_reg_acc = re.compile(r'accuracy\s=\s[0-9\.]+', flags=re.DOTALL)

def parse_train_line(line):
    """Parse a line from Caffe's training output

    Arguments
    ----------
    line : string
        Line to parse from training

    Returns
    ----------
    training_event : TrainingEvent
        A (possibly incomplete) CaffeEvent with the parsed information
    """
    line = line.decode('utf8')
    line = line.replace('\n', '')

    loss_match = re.findall(_reg_loss, line)
    acc_match = re.findall(_reg_acc, line)
    if loss_match:
        iteration_str, loss_str = loss_match[0].split(',')
        iter = int(iteration_str.replace('Iteration ', ''))
        loss = float(loss_str.replace('loss = ', ''))
        return TrainingEvent(iter, loss, None)
    elif acc_match:
        acc = float(acc_match[0].replace('accuracy = ', ''))
        return TrainingEvent(None, None, acc)
    else:
        return None
