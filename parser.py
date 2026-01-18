import nodes as n
from tokens import Token, TokenType
from result import ParseResult as Result
from pos import Position
from operators import Operator
from typing import Callable
from error import Error
from constants import KEYWORDS, TYPES
import types_ 

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = -1
        self.current_token: Token = self.advance()
        self.loops_inside: int = 0 # Number of loops the code is currently in
    def advance(self, amount: int = 1):
        self.index += amount
        if self.index >= len(self.tokens):
            self.current_token = self.tokens[-1]
        else:
            self.current_token = self.tokens[self.index]
        return self.current_token

    def parse(self) -> Result:
        if len(self.tokens) == 1:
            return Result()
        output = self.parse_top_level()
        if output.err:
            return output
        if self.index < len(self.tokens) - 1:
            return output.error(Error("Unexpected token. Expected EOF", self.current_token.pos_start, self.current_token.pos_end))
        return output
    
    # PARSING
    def parse_top_level(self) -> Result:
        "Parses a list of statements outside of functions"
        nodes = []
        res = Result()
        while self.current_token.token_type != TokenType.EOF:
            statement = res.process(self.parse_top_level_statement())
            if res.err: return res
            nodes.append(statement.get_success())
        return res.success(n.BlockNode(nodes, self.tokens[0].pos_start, self.tokens[-1].pos_end))
    def parse_top_level_statement(self) -> Result:
        "Parses a statement outside of any function"
        res = Result()
        if self.current_token.match_keyword(KEYWORDS["declare_func"]):
            return self.parse_func_decl()
        else:
            return res.error(Error("Unexpected token. ", self.current_token.pos_start, self.current_token.pos_end))
    def parse_block(self) -> Result:
        res = Result()
        if self.current_token.token_type == TokenType.L_BRACE:
            nodes = []
            pos_start = self.current_token.pos_start
            self.advance()
            while self.current_token.token_type != TokenType.R_BRACE:
                statement = res.process(self.parse_statement())
                if res.err: return res
                if statement.ok is None:
                    continue
                nodes.append(statement.get_success())
                if self.current_token.token_type == TokenType.EOF:
                    return res.error(Error("Expected '}'", self.current_token.pos_start, self.current_token.pos_end))
            pos_end = self.current_token.pos_end
            self.advance()
            return res.success(n.BlockNode(nodes, pos_start, pos_end))
        else:
            statement = res.process(self.parse_statement())
            if res.err: return res
            node = statement.get_success()
            return res.success(n.BlockNode([node], node.pos_start, node.pos_end))
    def parse_statement(self, semicolon_required = True) -> Result:
        res = Result()
        if self.current_token.match_keyword(KEYWORDS["declare_var"]):
            pos_start = self.current_token.pos_start
            self.advance()
            if self.current_token.token_type != TokenType.IDENTIFIER:
                return res.error(Error("Expected identifier", self.current_token.pos_start, self.current_token.pos_end))
            variable = self.current_token.value
            self.advance()
            if self.current_token.token_type != TokenType.COLON:
                return res.error(Error("Expected ':'", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()
            var_type = res.process(self.parse_type())
            if res.err: return res
            var_type = var_type.get_success()
            if self.current_token.token_type == TokenType.EQUALS:
                self.advance()
                value = res.process(self.parse_expression())
                if res.err: return res
                value = value.get_success()
            else:
                value = None
            
            if self.current_token.token_type != TokenType.SEMICOLON: 
                return res.error(Error("Expected semicolon", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()
            return res.success(n.VarDeclareNode(variable, var_type, value, pos_start, self.current_token.pos_end)) # pyright: ignore[reportArgumentType]
        elif self.current_token.token_type == TokenType.L_BRACE:
            return self.parse_block()
        elif self.current_token.token_type == TokenType.SEMICOLON:
            self.advance()
            return res
        elif self.current_token.match_keyword(KEYWORDS["return_value"]):
            pos_start = self.current_token.pos_start
            self.advance()
            if self.current_token.token_type == TokenType.SEMICOLON:
                pos_end = self.current_token.pos_end
                self.advance()
                return res.success(n.ReturnNode(None, pos_start, pos_end))
            value = res.process(self.parse_expression())
            if res.err: return res
            if self.current_token.token_type != TokenType.SEMICOLON: 
                return res.error(Error("Expected semicolon", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()
            return res.success(n.ReturnNode(value.get_success() , pos_start, value.get_success().pos_end))
        elif self.current_token.match_keyword(KEYWORDS["condition_main"]):
            return self.parse_conditional()
        elif self.current_token.match_keyword(KEYWORDS["loop_condition"]):
            pos_start = self.current_token.pos_start
            self.advance()
            condition = res.process(self.parse_expression())
            if res.err: return res
            self.loops_inside += 1
            block = res.process(self.parse_block())
            self.loops_inside -= 1
            if res.err: return res
            return res.success(n.WhileNode(condition.get_success(), block.get_success(), pos_start))
        elif self.current_token.match_keyword(KEYWORDS["control_next"]):
            if self.loops_inside == 0:
                return res.err(Error("Must be in loop", self.current_token.pos_start, self.current_token.pos_end))
            token = self.current_token
            self.advance()
            return res.success(n.ContinueNode(token.pos_start, token.pos_end))
        elif self.current_token.match_keyword(KEYWORDS["control_end"]):
            if self.loops_inside == 0:
                return res.error(Error("Must be in loop", self.current_token.pos_start, self.current_token.pos_end))
            token = self.current_token
            self.advance()
            return res.success(n.BreakNode(token.pos_start, token.pos_end))
        elif self.current_token.match_keyword(KEYWORDS["loop_threepart"]):
            pos_start = self.current_token.pos_start
            self.advance()
            if self.current_token.token_type != TokenType.L_PAREN:
                return res.error(Error("Expected '('", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()

            initial = res.process(self.parse_statement())
            if res.err: return res

            if self.current_token.token_type == TokenType.SEMICOLON:
                condition = Result()
            else:
                condition = res.process(self.parse_expression())
                if res.err: return res
                if self.current_token.token_type != TokenType.SEMICOLON: 
                    return res.error(Error("Expected semicolon", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()

            if self.current_token.token_type == TokenType.R_PAREN:
                iteration = Result()
            else:
                iteration = res.process(self.parse_statement(semicolon_required=False))
            if res.err: return res

            if self.current_token.token_type != TokenType.R_PAREN:
                return res.error(Error("Expected ')'", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()

            self.loops_inside += 1
            block = res.process(self.parse_block())
            if res.err: return res
            self.loops_inside -= 1

            return res.success(n.ForNode(initial.ok, condition.ok, iteration.ok, block.get_success(), pos_start))
        elif self.current_token.match_keyword(KEYWORDS["loop_iter"]):
            pos_start = self.current_token.pos_start
            self.advance()
            if self.current_token.token_type != TokenType.L_PAREN:
                return res.error(Error("Expected '('", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()
            if self.current_token.token_type != TokenType.IDENTIFIER:
                return res.error(Error("Expected variable name", self.current_token.pos_start, self.current_token.pos_end))
            var_name = self.current_token.value
            self.advance()
            if not self.current_token.match_keyword(KEYWORDS["value_in"]):
                return res.error(Error(f"Expected '{KEYWORDS["value_in"]}'", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()
            container = res.process(self.parse_expression())
            if res.err: return res
            container = container.get_success()
            if self.current_token.token_type != TokenType.R_PAREN:
                return res.error(Error("Expected ')'", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()
            block = res.process(self.parse_block())
            if res.err: return res
            block = block.get_success()
            return res.success(n.ForEachNode(var_name, container, block, pos_start))
        else:
            parse_res = res.process(self.parse_expression())
            if res.err: return res
            if semicolon_required:
                if self.current_token.token_type != TokenType.SEMICOLON: 
                    return res.error(Error("Expected semicolon", self.current_token.pos_start, self.current_token.pos_end))
                self.advance()
            return parse_res
    def parse_expression(self) -> Result:
        return self.parse_equality_expr()
    def parse_equality_expr(self) -> Result:
        return self.parse_binary_operation(
            self.parse_logical,
            [TokenType.EQEQ, TokenType.NOTEQ],
            [Operator.EQ, Operator.NOT_EQ]
        )
    def parse_logical(self) -> Result:
        return self.parse_binary_operation(
            self.parse_comparison,
            [TokenType.ANDAND, TokenType.PIPEPIPE],
            [Operator.LOGIC_AND, Operator.LOGIC_OR]
        )
    def parse_comparison(self) -> Result:
        return self.parse_binary_operation(
            self.parse_arithmetic,
            [TokenType.LT, TokenType.GE, TokenType.LE],
            [Operator.LT, Operator.GE, Operator.LE]
        )
    def parse_arithmetic(self) -> Result:
        return self.parse_binary_operation(
            self.parse_bitwise, [TokenType.PLUS, TokenType.MINUS], [Operator.ADD, Operator.SUB]
        )
    def parse_bitwise(self) -> Result:
        return self.parse_binary_operation(
            self.parse_term,
            [TokenType.AND, TokenType.PIPE, TokenType.CARET],
            [Operator.AND, Operator.OR, Operator.XOR]
        )
    def parse_term(self) -> Result:
        return self.parse_binary_operation(
            self.parse_factor, [TokenType.ASTERISK, TokenType.SLASH], [Operator.MUL, Operator.DIV]
        )
    def parse_factor(self) -> Result:
        res = Result()  
        
        if self.current_token.token_type in (TokenType.MINUS, TokenType.TILDE, TokenType.EXCLAMATION):
            op_token = self.current_token
            self.advance()
            value = res.process(self.parse_func_call())
            if res.err:
                return res
            return res.success(n.UnaryOpNode((
                Operator.LOGIC_NOT if op_token.token_type == TokenType.NOTEQ else
                Operator.NOT if op_token.token_type == TokenType.TILDE else
                Operator.NEG
            ), value.get_success(), self.current_token.pos_start))
        
        return self.parse_func_call()
    def parse_func_call(self) -> Result:
        res = Result()
        value = res.process(self.parse_atom())
        if res.err: return res
        if self.current_token.token_type != TokenType.L_PAREN:
            return value
        self.advance()
        args: list[n.Node] = []
        while self.current_token.token_type != TokenType.R_PAREN:
            arg = res.process(self.parse_expression())
            if res.err: return res
            args.append(arg.get_success())
            if self.current_token.token_type == TokenType.COMMA:
                self.advance()
                continue
            break
        if self.current_token.token_type != TokenType.R_PAREN:
            return res.error(Error("Expected ')'", self.current_token.pos_start, self.current_token.pos_end))
        pos_end = self.current_token.pos_end
        self.advance()
        return res.success(n.CallNode(value.get_success(), args, pos_end))
    def parse_atom(self) -> Result:
        res = Result()
        
        if self.current_token.token_type == TokenType.INT:
            res = res.success(n.IntNode(self.current_token))
            self.advance()
            return res
        elif self.current_token.token_type == TokenType.FLOAT:
            res = res.success(n.FloatNode(self.current_token))
            self.advance()
            return res
        elif self.current_token.token_type == TokenType.STR:
            res = res.success(n.StringNode(self.current_token))
            self.advance()
            return res
        elif self.current_token.token_type == TokenType.CHAR:
            res = res.success(n.CharNode(self.current_token))
            self.advance()
            return res
        elif self.current_token.token_type == TokenType.L_PAREN:
            self.advance()
            expr = res.process(self.parse_expression())
            if res.err:
                return res
            if self.current_token.token_type != TokenType.R_PAREN:
                return res.error(Error("Expected ')'", self.current_token.pos_start, self.current_token.pos_end))
            self.advance()
            return expr
        elif self.current_token.token_type == TokenType.IDENTIFIER:
            identifier = self.current_token
            self.advance()
            if self.current_token.token_type == TokenType.EQUALS:
                self.advance()
                value = res.process(self.parse_expression())
                if res.err: return res
                return res.success(n.VarAssignNode(identifier.value, value.get_success(), identifier.pos_start))
            return res.success(n.VarNode(identifier))
        elif self.current_token.token_type == TokenType.EOF:
            return res.error(Error("Unexpected EOF", self.current_token.pos_start, self.current_token.pos_end))
        elif self.current_token.token_type == TokenType.L_BRACKET:
            pos_start = self.current_token.pos_start
            self.advance()
            elements = []
            while True:
                element = res.process(self.parse_expression())
                if res.err: return res
                elements.append(element.get_success())
                if self.current_token.token_type != TokenType.COMMA:
                    break
                self.advance()
            if self.current_token.token_type != TokenType.R_BRACKET:
                return res.error(Error("Expected ']'", self.current_token.pos_start, self.current_token.pos_end))
            pos_end = self.current_token.pos_end
            self.advance()
            return res.success(n.ArrayNode(elements, pos_start, self.current_token.pos_end))
        elif self.current_token.match_keyword(KEYWORDS["bool_true"]):   
            token = self.current_token
            self.advance()
            return res.success(n.BoolNode(True, token.pos_start, token.pos_end))
        elif self.current_token.match_keyword(KEYWORDS["bool_false"]):
            token = self.current_token
            self.advance()
            return res.success(n.BoolNode(False, token.pos_start, token.pos_end))

        return res.error(Error("Unexpected token.", self.current_token.pos_start, self.current_token.pos_end))
    ####
    def parse_binary_operation(self, func: Callable, operator_tokentypes: list[TokenType], operators: list[Operator]) -> Result:
        res = Result()
        
        left = res.process(func())
        if res.err:
            return res
        if not self.current_token.token_type in operator_tokentypes: return left

        node: n.BinaryOpNode | None = None
        while self.current_token.token_type in operator_tokentypes:
            operator = operators[operator_tokentypes.index(self.current_token.token_type)]
            self.advance()
            right = res.process(func())
            if res.err:
                return res
            if node: 
                node = n.BinaryOpNode(node, operator, right.get_success())
            else:
                node = n.BinaryOpNode(left.get_success(), operator, right.get_success())
        return res.success(node)
    ####
    def parse_func_decl(self) -> Result:
        res = Result()
        pos_start = self.current_token.pos_start
        self.advance()
        if self.current_token.token_type == TokenType.IDENTIFIER:
            func_name = self.current_token.value
            self.advance()
        else:
            return res.error(Error("Expected identifier.", self.current_token.pos_start, self.current_token.pos_end))
        if self.current_token.token_type != TokenType.L_PAREN:
            return res.error(Error("Expected '('.", self.current_token.pos_start, self.current_token.pos_end))
        self.advance()
        args: dict[str, Type] = {}
        while self.current_token.token_type != TokenType.R_PAREN:
            if self.current_token.token_type != TokenType.IDENTIFIER: 
                return res.error(
                    Error("Expected identifier or ')'.", self.current_token.pos_start, self.current_token.pos_end)
                )
            arg_name = self.current_token.value
            self.advance()
            if self.current_token.token_type != TokenType.COLON: 
                return res.error(
                    Error("Expected ':'", self.current_token.pos_start, self.current_token.pos_end)
                )
            self.advance()
            type_ = res.process(self.parse_type())
            if res.err: return res
            args[arg_name] = type_.get_success()
            self.advance()
            if self.current_token.token_type != TokenType.COMMA:
                break
            self.advance()
            del arg_name
        self.advance()
        if self.current_token.token_type != TokenType.ARROW:
            return res.error(Error("Expected '->'.", self.current_token.pos_start, self.current_token.pos_end))
        self.advance()
        return_type = res.process(self.parse_type())
        if res.err: return res
        return_type = return_type.get_success()
        func_body = res.process(self.parse_block())
        if res.err: return res
        func_body = func_body.get_success()
        return res.success(n.FuncDeclNode(func_name, args, return_type, func_body, pos_start, func_body.pos_end))
    def parse_conditional(self) -> Result:
        res = Result()
        pos_start = self.current_token.pos_start
        self.advance()
        condition = res.process(self.parse_expression())
        if res.err: return res
        block = res.process(self.parse_block())
        if res.err: return res
        block = block.get_success()
        if self.current_token.match_keyword(KEYWORDS["condition_alt"]):
            alt = res.process(self.parse_conditional())
            if res.err: return res
            alt_case: n.IfNode = alt.get_success()
            alternate_cases: list[n.IfNode] = [alt_case] + alt_case.alternate_cases
            if alt_case.failure:
                failure = alt_case.failure
            else:
                failure = None
            alternate_cases[0].strip()
            return res.success(n.IfNode(condition.get_success(), block, alternate_cases, failure, pos_start, alt_case.pos_end))
        elif self.current_token.match_keyword(KEYWORDS["condition_fail"]):
            self.advance()
            else_block = res.process(self.parse_block())
            if res.err: return res
            else_block = else_block.get_success()
            return res.success(n.IfNode(condition.get_success(), block, [], else_block, pos_start, else_block.pos_end))
        else:
            return res.success(n.IfNode(condition.get_success(), block, [], None, pos_start, block.pos_end))
    def parse_type(self) -> Result:
        res = Result()
        if self.current_token.token_type == TokenType.TYPE:
            type_elem = TYPES[self.current_token.value]
            self.advance()
            return res.success(types_.Type(types_.BasicType(type_elem)))
        elif self.current_token.token_type == TokenType.L_BRACKET:
            pos_start = self.current_token.pos_start
            self.advance()
            element_type = res.process(self.parse_type())
            if res.err: return res
            if self.current_token.token_type != TokenType.R_BRACKET:
                return res.error(Error("Expected ']'.", self.current_token.pos_start, self.current_token.pos_end))
            pos_end = self.current_token.pos_end
            self.advance()
            return res.success(types_.Type(types_.ArrayType(element_type.get_success())))
        else:
            return res.error(Error("Expected type", self.current_token.pos_start, self.current_token.pos_end))