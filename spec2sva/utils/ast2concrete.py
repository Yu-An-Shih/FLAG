
def ast_to_ltl(ast: dict) -> str:
    ### Convert the AST to LTL formula ###

    if ast['type'] == 'variable':
        return ast['variable']
    elif ast['type'] == 'operator' or ast['type'] == 'basic':
        operands = " ".join(ast_to_ltl(operand) for operand in ast['operands'])
        return f"({ast['operator']} {operands})"
    else:
        raise ValueError(f"Invalid AST node type: {ast['type']}")


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