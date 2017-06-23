'''Simple test file to check whether tests go smooth'''


def func(x):
    '''Simple addition function'''
    return x + 1


def test_answer():
    '''Simple test for addition function'''
    assert func(3) == 4
