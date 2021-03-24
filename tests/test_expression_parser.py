import pytest

from sprint_stats.expression_parser import Value_Expression, Const_Expression, Binary_Expression, parse_expression

@pytest.fixture
def evaluation_object():
    return {
        "key_1": 3,
        "key_2": 5
    }

def test_const_expression(evaluation_object):
    v = Const_Expression(5)
    assert v.evaluate(evaluation_object) == 5

def test_value_expression(evaluation_object):
    v = Value_Expression("key_1")
    assert v.evaluate(evaluation_object) == 3

@pytest.mark.parametrize("operation,expected",[('+',15),('-',5),('*',50),('/',2.0)])
def test_binary_expression(evaluation_object, operation, expected):
    left = Const_Expression(10)
    right = Value_Expression("key_2")
    assert Binary_Expression(operation, left, right).evaluate(evaluation_object) == expected


def test_parse_expression_value():
    assert isinstance(parse_expression(4), Const_Expression)

def test_parse_expression_key():
    assert isinstance(parse_expression("key_2"), Value_Expression)

def test_parse_expression_binary(evaluation_object):
    json_representation = {
        "operation": '+',
        "expression_1": 4,
        "expression_2": {
            "operation": '*',
            "expression_1": "key_1",
            "expression_2": "key_2"
        }
    }
    expression = parse_expression(json_representation)
    assert isinstance(expression, Binary_Expression)
    assert expression.evaluate(evaluation_object) == 19