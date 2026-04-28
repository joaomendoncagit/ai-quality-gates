from calculator import add, divide
import pytest

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(6, 2) == 3
    assert isinstance(divide(6, 2), int)

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(6, 0)