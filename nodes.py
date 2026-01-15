import pos
import operators
import tokens
import types_

class Node:
    def __init__(self, pos_start: pos.Position, pos_end: pos.Position):
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return "(Node)"
    
class IntNode(Node):
    def __init__(self, token: tokens.Token):
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end
        self.value = token.value

    def __repr__(self):
        return f"(int {self.value})"

class FloatNode(Node):
    def __init__(self, token: tokens.Token):
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end
        self.value = token.value

    def __repr__(self):
        return f"(float {self.value})"

class StringNode(Node):
    def __init__(self, token: tokens.Token):
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end
        self.value = token.value

    def __repr__(self):
        return f"(str {self.value})"

class BinaryOpNode(Node):
    "Used for binary operations"
    def __init__(self, left: Node, operator: operators.Operator, right: Node):
        self.left = left
        self.operator = operator
        self.right = right
        self.pos_start = left.pos_start
        self.pos_end = right.pos_end
    
    def __repr__(self):
        return f"({self.left} {self.operator.name} {self.right})"

class UnaryOpNode(Node):
    "Used for unary operations"
    def __init__(self, operator: operators.Operator, value: Node, pos_start: pos.Position):
        self.value = value
        self.operator = operator
        self.pos_start = pos_start
        self.pos_end = value.pos_end
    
    def __repr__(self):
        return f"({self.operator.name} {self.value})"

class CharNode(Node):
    def __init__(self, token: tokens.Token):
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end
        self.value = token.value

    def __repr__(self):
        return f"(char {self.value})"

class VarNode(Node):
    def __init__(self, token: tokens.Token):
        self.var_name = token.value
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end
    def __repr__(self):
        return f"(var {self.var_name})"

class VarAssignNode(Node):
    def __init__(self, var_name: str, value: Node, pos_start: pos.Position):
        self.var_name = var_name
        self.value = value
        self.pos_start = pos_start
        self.pos_end = value.pos_end
    def __repr__(self):
        return f"(set {self.var_name} = {self.value})"

class VarDeclareNode(Node):
    def __init__(self, var_name: str, var_type: types_.Type, value: Node | None, pos_start: pos.Position, pos_end = pos.Position):
        self.var_name = var_name
        self.var_type = var_type
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return f"[variable {self.var_name}: {self.var_type}" + (
            f" = {self.value}]" if self.value else "]"
        )

class BlockNode(Node):
    def __init__(self, nodes: list[Node], pos_start: pos.Position, pos_end: pos.Position):
        self.nodes = nodes
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return f"(block: {self.nodes})"

class FuncDeclNode(Node):
    def __init__(self, name: str, args: dict[str, types_.Type], return_type: types_.Type, body: BlockNode, pos_start: pos.Position, pos_end: pos.Position):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return f"(function {self.name}({self.args})) -> {self.return_type} {self.body})"

class ReturnNode(Node):
    def __init__(self, value: Node, pos_start: pos.Position):
        self.value = value
        self.pos_start = pos_start
        self.pos_end = value.pos_end
    def __repr__(self):
        return f"(return {self.value})"

class CallNode(Node):
    def __init__(self, node: Node, arguments: list[Node], pos_end: pos.Position):
        self.node = node
        self.arguments = arguments
        self.pos_end = pos_end
        self.pos_start = node.pos_start
    def __repr__(self):
        return f"(call {self.node} {self.arguments})"

class IfNode(Node):
    def __init__(self, condition: Node, success: Node, alternate_cases, failure: BlockNode | None, pos_start, pos_end):
        self.condition = condition
        self.success = success
        self.alternate_cases: list[IfNode] = alternate_cases
        self.failure = failure
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return (
            f"[if {self.condition} {self.success}"
            + (f" alt {self.alternate_cases}" if self.alternate_cases else "")
            + (f" else {self.failure}" if self.failure else "")
            + "]"
        )
    def strip(self):
        self.alternate_cases = []
        self.failure = None

class WhileNode(Node):
    def __init__(self, condition: Node, block: Node, pos_start: pos.Position):
        self.cond = condition
        self.block = block
        self.pos_start = pos_start
        self.pos_end = block.pos_end
    def __repr__(self):
        return (
            f"[while {self.cond} {self.block}]"
        )

class ContinueNode(Node):
    def __init__(self, pos_start: pos.Position, pos_end: pos.Position):
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return (
            f"[continue]"
        )

class BreakNode(Node):
    def __init__(self, pos_start: pos.Position, pos_end: pos.Position):
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return (
            f"[break]"
        )

class ForNode(Node):
    def __init__(self, initial: Node | None, condition: Node | None, iteration: Node | None, block: Node, pos_start: pos.Position):
        self.pos_start = pos_start
        self.pos_end = block.pos_end
        self.init = initial
        self.cond = condition
        self.iter = iteration
        self.block = block
    def __repr__(self):
        return (
            f"[for [{self.init}; {self.cond}; {self.iter}] {self.block}]"
        )

class ArrayNode(Node): 
    def __init__(self, elements: list[Node], pos_start: pos.Position, pos_end: pos.Position):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        return (
            f"(array {self.elements})" 
        )
   
class ForEachNode(Node):
    def __init__(self, var_name: str, container: Node, block: Node, pos_start: pos.Position):
        self.pos_start = pos_start
        self.pos_end = block.pos_end
        self.var_name = var_name
        self.container = container
        self.block = block
    def __repr__(self):
        return (
            f"[foreach [{self.var_name} in {self.container}] {self.block}]"
        )
