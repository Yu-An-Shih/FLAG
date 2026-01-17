# import re
import sys

def ast_to_sva(ast: dict) -> str:
    ### Convert the AST to SVA ###
    ### NOTE: Assumes the AST is in property format. ###
    # WARNING: This function should be modified or extended if new operators are added to the grammar

    def _binary(val: str, width: str = '1') -> str:
        val = int(val)
        width = int(width)
        return f"{width}'b{val:0{width}b}"
    
    match ast['operator']:
        # Propositions
        case '==' | '!=':
            if ast['operands'][0]['type'] == 'signal':
                return f"({ast['operands'][0]['value']} {ast['operator']} {_binary(ast['operands'][1]['value'])})"
            else:   # ast['operands'][0]['type'] == 'word'
                return f"({ast['operands'][0]['value']} {ast['operator']} {_binary(ast['operands'][1]['value'], ast['operands'][0]['width'])})"
        case '$rose' | '$fell' | '$stable':
            return f"{ast['operator']}({ast['operands'][0]['value']})"
        # Logical
        case 'And':
            return "(" + " && ".join(ast_to_sva(operand) for operand in ast['operands']) + ")"
        case 'Or':
            return "(" + " || ".join(ast_to_sva(operand) for operand in ast['operands']) + ")"
        case 'Implies':
            return f"{ast_to_sva(ast['operands'][0])} |-> {ast_to_sva(ast['operands'][1])}"
        # Temporal
        case 'X':
            return f"##1 {ast_to_sva(ast['operands'][0])}"
        case 'F':
            return f"##[0:$] {ast_to_sva(ast['operands'][0])}"
        case 'G':
            return ast_to_sva(ast['operands'][0])
        # Unknown
        case _:
            raise ValueError(f"Unknown operator: {ast['operator']}")


def ast_to_nl(ast: dict, IsTemplate: bool) -> str:
    ### Convert the AST to natural language ###
    # WARNING: This function should be modified or extended if new operators are added to the grammar
    
    def _level(val: str) -> str:
        val = int(val)
        assert val in {0, 1}
        return 'LOW' if val == 0 else 'HIGH'
    
    def _binary(val: str, width: str) -> str:
        val = int(val)
        width = int(width)
        return f"{width}'b{val:0{width}b}"
    
    match ast['operator']:
        # Propositions
        case '==' | '!=':
            if IsTemplate:
                return f"[{ast['operands'][0]['type']}] {ast['operator']} [{ast['operands'][1]['type']}]"
            else:
                if ast['operands'][0]['type'] == 'signal':
                    assert ast['operator'] == '=='  # Only '==' is allowed for signals to avoid redundancy
                    return f"{ast['operands'][0]['value']} is {_level(ast['operands'][1]['value'])}"
                else:
                    assert ast['operands'][0]['type'] == 'word'
                    return f"{ast['operands'][0]['value']} {ast['operator']} {_binary(ast['operands'][1]['value'], ast['operands'][0]['width'])}"
        case '$rose':
            if IsTemplate:
                return f"[{ast['operands'][0]['type']}] changes from LOW to HIGH"
            else:
                return f"{ast['operands'][0]['value']} changes from LOW to HIGH"
        case '$fell':
            if IsTemplate:
                return f"[{ast['operands'][0]['type']}] changes from HIGH to LOW"
            else:
                return f"{ast['operands'][0]['value']} changes from HIGH to LOW"
        case '$stable':
            if IsTemplate:
                return f"[{ast['operands'][0]['type']}] remains stable"
            else:
                return f"{ast['operands'][0]['value']} remains stable"
        # Logical
        case 'And' | 'Or':
            return f" {ast['operator'].lower()} ".join(ast_to_nl(operand, IsTemplate) for operand in ast['operands'])
        case 'Implies':
            return f"If {ast_to_nl(ast['operands'][0], IsTemplate)}, then {ast_to_nl(ast['operands'][1], IsTemplate)}."
        # Temporal
        case 'X':
            return f"{ast_to_nl(ast['operands'][0], IsTemplate)} in the next cycle"
        case 'F':
            return f"{ast_to_nl(ast['operands'][0], IsTemplate)} eventually"
        case 'G':
            return ast_to_nl(ast['operands'][0], IsTemplate)
        # Unknown
        case _:
            raise ValueError(f"Unknown operator: {ast['operator']}")


def ast_to_ltl(ast: dict, IsTemplate: bool) -> str:
    ### Convert the AST to LTL formula ###

    if ast['type'] == 'basic':
        if IsTemplate:
            # TODO: Add '[]' for template variables?
            operands = " ".join(f"[{operand['type']}]" for operand in ast['operands'])
        else:
            operands = " ".join(operand['value'] for operand in ast['operands'])
    elif ast['type'] == 'operator':
        operands = " ".join(ast_to_ltl(operand, IsTemplate) for operand in ast['operands'])
    else:
        raise ValueError(f"Invalid AST node type: {ast['type']}")
    
    return f"({ast['operator']} {operands})"


# def ltl_to_ast(ltl: str) -> dict:
#     ### Convert the LTL formula to AST ###
#     # WARNING: This function should be extended/modified if operators are added/modified

#     def tokenize(expression: str) -> list:
#         ### Tokenizes the input expression into a list of symbols and parentheses. ###
#         tokens = re.findall(r'\(|\)|[^\s()]+', expression)
#         return tokens
    
#     def parse(tokens: list) -> list:
#         ### Parses the tokenized input into a nested list representation. ###
        
#         token = tokens.pop(0)

#         if token == '(':
#             # Start a new list (for the operators)
#             parsed_expr = []
#             while tokens[0] != ')':
#                 parsed_expr.append(parse(tokens))
#             tokens.pop(0)  # Remove closing ')'
#             return parsed_expr
#         else:
#             return token

#     def build_ast(parsed_expr: list) -> dict:
#         ### Converts the parsed list structure into an AST dictionary. ###
#         # WARNING: This function should be extended/modified if operators are added/modified
        
#         operator = parsed_expr[0]
        
#         if operator in {"And", "Or", "Implies", "X", "F", "G"}:
#             return {
#                 "type": "operator",
#                 "operator": operator,
#                 "operands": [build_ast(operand) for operand in parsed_expr[1:]]
#             }
#         elif operator in {"==", "!=", "$rose", "$fell", "$stable"}:
#             return {
#                 "type": "basic",
#                 "operator": operator,
#                 "operands": [
#                     {"type": "variable", "variable": parsed_expr[i]} for i in range(1, len(parsed_expr))
#                 ]
#             }
#         else:
#             raise ValueError(f"Unknown operator: {operator}")
    
#     tokens = tokenize(ltl)
#     parsed_expr = parse(tokens)
#     return build_ast(parsed_expr)
