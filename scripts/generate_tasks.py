"""Use this script to generate tasks via random hyperparameter search. This is a first pass, but eventually
something similar to this will be added to the Mri server. Also worth noting is that this may be spun off into
a separate module if it's useful enough

To use, first copy the configuration example to `config` and add your own values. The mother model and solver
should simply replace any fields to be replaced by %{field-name}%. Then, create the hyperparameter file:

field-name: 1,2,3,4
field-name2: 0.23, 1.2, 5.4

The field names can be in either the model or solver, just use unique names
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import configparser
import os
import uuid
import random
import json
import argparse


def create_dir(path):
    """Helper to create dir if one doesn't exist"""
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


class TaskCreator(object):
    def __init__(self, config_file):
        """New TaskCreator with given config file

        Arguments
        ----------
        config_file : string
            filename of configuration file
        """
        # Get config information
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.folder = self.config.get('generate-tasks', 'task_folder')
        self.hyperparams = self.config.get('generate-tasks', 'hyperparams')

        model = self.config.get('generate-tasks', 'mother_model')
        solver = self.config.get('generate-tasks', 'mother_solver')

        # Read in mother files
        with open(model) as m:
            self.model = str(m.read())
        with open(solver) as s:
            self.solver = str(s.read())

    def sample(self):
        """Sample a random permutation of hyperparameters

        Arguments
        ----------
        None
        """
        sample_dict = {}
        with open(self.hyperparams) as f:
            for line in f:
                task, items = line.split(':')
                params = [item.strip() for item in items.split(',')]
                sample_dict[task] = random.choice(params)
        return sample_dict

    def create_task(self, **kwargs):
        """Create a task from random search with the given kwargs

        Arguments
        ----------
        kwargs : dict
            Replacements to make in model and solver template files

        Returns
        ----------
        task_path : string
            Name and path of this task
        """
        # Setup the directory structure if it doesn't exist
        create_dir(self.folder)
        task_name = str(uuid.uuid4())
        # Create the new task
        task_path = os.path.join(self.folder, task_name)
        create_dir(task_path)
        snapshot_path = os.path.join(task_path, 'snapshots')
        create_dir(snapshot_path)
        model_location = os.path.join(task_path, 'model.prototxt')
        solver_location = os.path.join(task_path, 'solver.prototxt')
        # Create a new model and solver
        new_model = self.model
        new_solver = self.solver
        for key in kwargs:
            search_str = '%{{{0}}}%'.format(key)
            new_model = new_model.replace(search_str, kwargs[key])
            new_solver = new_solver.replace(search_str, kwargs[key])
        # Replace net and snapshot_prefix in solver
        snapshot_prefix = '\"{}\"'.format(os.path.join(snapshot_path, 'snapshots'))
        net = '\"{}\"'.format(model_location)

        new_solver = self.replace_solver_param(new_solver, 'net', net)
        new_solver = self.replace_solver_param(new_solver, 'snapshot_prefix', snapshot_prefix)
        # Write files
        with open(model_location, 'w') as f:
            f.write(new_model)
        with open(solver_location, 'w') as f:
            f.write(new_solver)
        # Create task file
        train_directive = [{'type': 'train', 'parameters': {'model': model_location, 'solver': solver_location}}]
        task_file = {'directives': train_directive, 'name': str(kwargs), 'id': task_name}
        with open(os.path.join(task_path, 'task.json'), 'w') as f:
            json.dump(task_file, f, indent=4)
        return task_path

    @staticmethod
    def replace_solver_param(solver, param, new_val):
        """Replace a parameter from the solver of this task.

        Note: We should probably use a similar method so the user doesn't have to make a special
        solver and model template, but for now we'll just use this for the net and snapshot_prefix
        parts of the solver file.

        Arguments
        ----------
        param : string
            Name of the parameter to replace

        new_val : string
            Replacement value

        Returns
        ----------
        replaced_solver : string
            A copy of the solver file but with the replacement made
        """
        replaced_solver = ""
        for line in solver.splitlines():
            new_line = line
            if ':' in line:
                p, value = line.split(':')
                if p == param:
                    new_line = '{0}: {1}'.format(param, new_val)
            replaced_solver += new_line + os.linesep
        return replaced_solver


def main():
    parser = argparse.ArgumentParser(description='Create tasks for Mri')
    parser.add_argument('-n')
    arg = parser.parse_args()
    n_samps = int(arg.n)

    task = TaskCreator('config')
    task_list = os.path.join(task.folder, 'generated_tasks.txt')
    with open(task_list, 'w') as f:
        for n in range(n_samps):
            samp = task.sample()
            task_path = task.create_task(**samp)
            full_path = os.path.join(task_path, 'task.json')
            f.write(full_path)
            f.write(os.linesep)


if __name__ == "__main__":
    main()
