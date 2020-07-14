import os
import random
import re
import string
from subprocess import getstatusoutput

prg = './driver.py'


# --------------------------------------------------
def test_exists() -> None:
    """Program exists"""

    assert os.path.isfile(prg)


# --------------------------------------------------
def test_invalid_language() -> None:
    """Rejects invalid language"""

    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    assert os.path.isdir(plugins_dir)
    lang = random_string()
    name = random_string()
    rv, out = getstatusoutput(f'PYTHONPATH={plugins_dir} {prg} {lang} {name}')
    assert rv != 0
    assert re.search(f"argument lang: invalid choice: '{lang}'", out)


# --------------------------------------------------
def test_english() -> None:
    """Test greet in English"""

    name = random_string()
    run('english', name, f'Hello, {name}!')


# --------------------------------------------------
def test_spanish() -> None:
    """Test greet in Spanish"""

    name = random_string()
    run('spanish', name, f'¡Hola, {name}!')


# --------------------------------------------------
def random_string():
    """generate a random string"""

    k = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))


# --------------------------------------------------
def run(lang: str, name: str, expected: str) -> None:
    """Run program with options"""

    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    assert os.path.isdir(plugins_dir)
    rv, out = getstatusoutput(f'PYTHONPATH={plugins_dir} {prg} {lang} {name}')
    assert rv == 0
    assert out == expected
