import random
import string
from greet_english import greet


# --------------------------------------------------
def test_greet() -> None:
    """Test greet in English"""

    for _ in range(10):
        name = random_string()
        assert greet(name) == f"Hello, {name}!"


# --------------------------------------------------
def random_string():
    """generate a random string"""

    k = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))
