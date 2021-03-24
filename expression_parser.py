
class Expression:
    def evaluate(self, obj):
        pass

class Expression_Exception(Exception):

    def __init__(self, exp, step, message):
        self.exp = exp
        self.step = step
        super().__init__(message)
    
    def __str__(self):
        return "Expression {}: {} failed: {}".format(self.exp, self.step, super().__str__())


class Const_Expression(Expression):
    
    def __init__(self, value):
        self.value = value

    def evaluate(self, obj):
        return self.value

class Value_Expression(Expression):
    
    def __init__(self, key):
        self.key = key

    def evaluate(self, obj):
        if not self.key in obj:
           raise Expression_Exception(self, "evaluate", "key {} is not defined in object".format(self.key))
        value = obj[self.key]
        if not isinstance(value, (int,float)):
           raise Expression_Exception(self, "evaluate", "key {} is not a valid value".format(self.key))
        return value

class Binary_Expression(Expression):

    def __init__(self, operation : str, left : Expression, right: Expression):
        if operation not in ["+","-","*","/"]:
            raise Exception("operation {} not supported".format(operation))
        
        self.operation = operation
        self.left = left
        self.right = right

    def evaluate(self,obj):
        return eval("l" + self.operation + "r", {"l": self.left.evaluate(obj), "r": self.right.evaluate(obj)})

def parse_expression(json_representation):
    # is a constant
    if isinstance(json_representation, (int, float)):
        return Const_Expression(json_representation)
    # is a string --> a key of the object
    if isinstance(json_representation, str):
        return Value_Expression(json_representation)
    # is a nested expression
    if not "operation" in json_representation:
        raise Expression_Exception(json_representation, "parsing", "json representation has no field operation")
    
    if not "expression_1" in json_representation:
        raise Expression_Exception(json_representation, "parsing", "with a binary expression, an expression_1 is required")
    expression_left = parse_expression(json_representation["expression_1"])
    # only binary expression for the moment
    if not "expression_2" in json_representation:
        raise Expression_Exception(json_representation, "parsing", "with a binary expression, an expression_2 is required")
    expression_right = parse_expression(json_representation["expression_2"])

    try:
        return Binary_Expression(json_representation["operation"], expression_left, expression_right)
    except Exception as exc:
        raise Expression_Exception(json_representation, "parsing", exc.__str__())
    