import random
import string
from greet_spanish import greet


# --------------------------------------------------
def test_greet() -> None:
    """Test greet"""

    for _ in range(10):
        name = random_string()
        assert greet(name) == f"¡Hola, {name}!"


# --------------------------------------------------
def random_string():
    """generate a random string"""

    k = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))
