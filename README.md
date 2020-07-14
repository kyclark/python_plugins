# Exploring dynamic loading of Python plugins

While working with the [AgPipeline's](https://github.com/AgPipeline) [Greeness Transformer](https://github.com/AgPipeline/transformer-rgb-indices), I noticed there is a hierarchy of modules that are created by building Docker images from a series of base images.
The goal of this layering is to allow developers to plugin a new module.
For instance, the Greeness Transformer has an [algorithm_rgb.py](https://github.com/AgPipeline/transformer-rgb-indices/blob/master/algorithm_rgb.py) file that implements a "calculate()" function.
The function accepts a pixel array of image data and returns a list of integer values.

The code that calls the "calculate()" and passes the pixel values read from a file exists in [Plot Base RGB transformer.py](https://github.com/AgPipeline/plot-base-rgb/blob/master/transformer.py).
This module imports an "algorithm_rgb" module which doesn't exist in this repo.
The transformer assumes there will be an `algorithm_rgb.py` file present when the code is run which can be imported at run-time and which contains a "calculate()" function (among other attributes).

One downside to haveing no `algorithm_rgb.py` module in the transformer repo means that the interaction of these two modules cannot be tested.
The only way to test the Greeness Transformer in context is to build a Docker container that is based on the other nested containers such that the transformer and the algorithm modules can be brought together.

The user-interface/entrypoint/[code that calls the transformer](https://github.com/AgPipeline/base-docker-support/blob/master/base-image/entrypoint.py) lives in [another repo](https://github.com/AgPipeline/base-docker-support).

A schematic of the Docker layers/dependencies:

```
transformer-rgb-indices <1>
          |
          v
    plot-base-rgb <2>
          |
          v
  base-docker-support <3>

```

1. The "algorithm_rgb.py" goes here and should have a "calculate()" function.
2. The "transformer.py" lives here and calls "calculate()".
3. The "entrypoint.py" lives here and uses the transformer.

## Using a plugin architecture

Many Python modules (e.g., Flask) use a "plugin" style of allowing people to add extensions to packages.
The "Python Packaging User Guide" has an entry on [Creating and discovering plugins](https://packaging.python.org/guides/creating-and-discovering-plugins/) with some intersting suggestions.

Following the suggestions there, I explored how to create a Python program that will create a greeting for a given language.
In the "plugins" directory, you'll notice there are modules called `greet_english.py` and `greet_spanish.py`.

```
$ ls -1 plugins/
Makefile
greet_english.py
greet_spanish.py
test_greet_english.py
test_greet_spanish.py
```

These modules include tests which can be discovered and run using `pytest`:

```
$ pytest -v
============================= test session starts ==============================
...

test_greet_english.py::test_greet PASSED                                 [ 50%]
test_greet_spanish.py::test_greet PASSED                                 [100%]

============================== 2 passed in 0.01s ===============================
```

The `driver.py` program is the user interface:

```
$ ./driver.py -h
usage: driver.py [-h] lang name

Run function from imported module

positional arguments:
  lang        Language to use
  name        Name to greet

optional arguments:
  -h, --help  show this help message and exit
```

It will detect any "greet_" module at run-time, so you cannot, for instance, request a greeting in German:

```
$ ./driver.py german Bert
usage: driver.py [-h] lang name
driver.py: error: argument lang: invalid choice: 'german' \
(choose from 'english', 'spanish')
```

If you select from either "english" or "spanish," you will get an appropriate greeting:

```
$ ./driver.py english Ernie
Hello, Ernie!
$ ./driver.py spanish Bert
¡Hola, Bert!
```

This happens because the `driver.py` will use the `greet()` function in these module to produce an internationalized salutation.

```
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
    plugins = { <1>
        name.replace('greet_', ''): importlib.import_module('plugins.' + name)
        for _, name, _ in pkgutil.iter_modules(path=[plugin_dir])
        if name.startswith('greet_')
    }

    args = get_args(plugins)

    print(plugins[args.language].greet(args.name)) <2>


# --------------------------------------------------
if __name__ == '__main__':
    main()
```

1. This looks in the "plugins" directory that lives in the same directory as the `driver.py` file.
2. This calls the `greet()` function in the given plugin passing the "name" value.

There is a test for this program:

```
$ pytest -v test_driver.py
============================= test session starts ==============================
...

test_driver.py::test_exists PASSED                                       [ 25%]
test_driver.py::test_invalid_language PASSED                             [ 50%]
test_driver.py::test_english PASSED                                      [ 75%]
test_driver.py::test_spanish PASSED                                      [100%]

============================== 4 passed in 0.18s ===============================
```

## Adding a new plugin

If we wanted to implement a "german" greeting, we can add a `plugins/greeting_german.py` module that has a `greet()` function.
If you switch the repo to the "german" branch, you'll see [just that](https://github.com/kyclark/python_plugins/blob/german/plugins/greet_german.py):

```
$ git checkout german
M	README.md
Switched to branch 'german'
$ cat plugins/greet_german.py
def greet(name: str) -> str:
    """Say hello to the name"""

    return f"Hallo, {name}!"
```

Following the pattern of the tests for English and Spanish, we can also create a test for German:

```
$ cat plugins/test_greet_german.py
import random
import string
from greet_german import greet


# --------------------------------------------------
def test_greet() -> None:
    """Test greet in German"""

    for _ in range(10):
        name = random_string()
        assert greet(name) == f"Hallo, {name}!"


# --------------------------------------------------
def random_string():
    """generate a random string"""

    k = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))
```

And now we can use a German greeting:

```
$ ./driver.py german Oscar
Hallo, Oscar!
```

But not yet French:

```
$ ./driver.py french Beeker
usage: driver.py [-h] lang name
driver.py: error: argument lang: invalid choice: 'french' \
(choose from 'english', 'german', 'spanish')
```

## Application to Transformers

The goal is to create a single repository with all the code necessary to test the integration of a new plugin for the AgPipeline transformers.
I can imagine a repo with a similar "algorithms" directory containing sample implementations of algorithms and tests as guides.
Developers of a new "algorithm" would be instructuted to "fork" this base repo and add their new code as a something like `algorithm/greeness.py` (and a test suite).

Just as there is a `driver.py` in this sample repo that serves as the user interface, the `entrypoint.py` would live in the repo and could load transformers and algorithms dynamically as needed.
The advantage to the developer would be a much simplified architecture with a single repository containing all the code necessary to test a new algorithm *in context* -- that is, by actually running the program, passing in files as arguments, and seeing the output.

## Author

Ken Youens-Clark <kyclark@gmail.com>
