#!/usr/bin/env python3
"""Run function from imported module"""

import argparse
import importlib
import os
import pkgutil
from typing import NamedTuple, Callable, Dict


class Args(NamedTuple):
    language: str
    name: str


# --------------------------------------------------
def get_args(plugins: Dict[str, Callable]) -> Args:
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Run function from imported module',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('language',
                        type=str,
                        metavar='lang',
                        help='Language to use',
                        choices=plugins.keys())

    parser.add_argument('name',
                        type=str,
                        metavar='name',
                        help='Name to greet')

    args = parser.parse_args()

    return Args(args.language, args.name)


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    cwd = os.path.realpath(__file__)
    plugin_dir = os.path.join(os.path.dirname(cwd), 'plugins')
    plugins = {
        name.replace('greet_', ''): importlib.import_module('plugins.' + name)
        for _, name, _ in pkgutil.iter_modules(path=[plugin_dir])
        if name.startswith('greet_')
    }

    args = get_args(plugins)

    print(plugins[args.language].greet(args.name))


# --------------------------------------------------
if __name__ == '__main__':
    main()
