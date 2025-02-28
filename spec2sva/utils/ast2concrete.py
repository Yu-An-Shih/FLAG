import re

def ast_to_nl(ast: dict) -> str:
    ### Convert the AST to natural language ###
    # WARNING: This function should be modified or extended if new operators are added to the grammar
    
    if ast['type'] == 'variable':
        return ast['variable']
    elif ast['type'] == 'operator' or ast['type'] == 'basic':
        match ast['operator']:
            # Propositions
            case '==' | '!=':
                return f"{ast_to_nl(ast['operands'][0])} {ast['operator']} {ast_to_nl(ast['operands'][1])}"
            case '$rose' | '$fell' | '$stable':
                return f"{ast['operator']}({ast_to_nl(ast['operands'][0])})"
            # Logical
            case 'And' | 'Or':
                return f" {ast['operator'].lower()} ".join(ast_to_nl(operand) for operand in ast['operands'])
                #return f"{ast_to_nl(ast['operands'][0])} {ast['operator'].lower()} {ast_to_nl(ast['operands'][1])}"
            case 'Implies':
                return f"If {ast_to_nl(ast['operands'][0])}, then {ast_to_nl(ast['operands'][1])}."
            # Temporal
            case 'X':
                return f"{ast_to_nl(ast['operands'][0])} in the next cycle"
            case 'F':
                return f"{ast_to_nl(ast['operands'][0])} eventually"
            case 'G':
                return ast_to_nl(ast['operands'][0])
            # Unknown
            case _:
                raise ValueError(f"Unknown operator: {ast['operator']}")

        operands = " ".join(ast_to_ltl(operand) for operand in ast['operands'])
        return f"({ast['operator']} {operands})"
    else:
        raise ValueError(f"Invalid AST node type: {ast['type']}")


def ast_to_ltl(ast: dict) -> str:
    ### Convert the AST to LTL formula ###

    if ast['type'] == 'variable':
        return ast['variable']
    elif ast['type'] == 'operator' or ast['type'] == 'basic':
        operands = " ".join(ast_to_ltl(operand) for operand in ast['operands'])
        return f"({ast['operator']} {operands})"
    else:
        raise ValueError(f"Invalid AST node type: {ast['type']}")


def ltl_to_ast(ltl: str) -> dict:
    ### Convert the LTL formula to AST ###
    # WARNING: This function should be extended/modified if operators are added/modified

    def tokenize(expression: str) -> list:
        ### Tokenizes the input expression into a list of symbols and parentheses. ###
        tokens = re.findall(r'\(|\)|[^\s()]+', expression)
        return tokens
    
    def parse(tokens: list) -> list:
        ### Parses the tokenized input into a nested list representation. ###
        
        token = tokens.pop(0)

        if token == '(':
            # Start a new list (for the operators)
            parsed_expr = []
            while tokens[0] != ')':
                parsed_expr.append(parse(tokens))
            tokens.pop(0)  # Remove closing ')'
            return parsed_expr
        else:
            return token

    def build_ast(parsed_expr: list) -> dict:
        ### Converts the parsed list structure into an AST dictionary. ###
        # WARNING: This function should be extended/modified if operators are added/modified
        
        operator = parsed_expr[0]
        
        if operator in {"And", "Or", "Implies", "X", "F", "G"}:
            return {
                "type": "operator",
                "operator": operator,
                "operands": [build_ast(operand) for operand in parsed_expr[1:]]
            }
        elif operator in {"==", "!=", "$rose", "$fell", "$stable"}:
            return {
                "type": "basic",
                "operator": operator,
                "operands": [
                    {"type": "variable", "variable": parsed_expr[i]} for i in range(1, len(parsed_expr))
                ]
            }
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    tokens = tokenize(ltl)
    parsed_expr = parse(tokens)
    return build_ast(parsed_expr)
