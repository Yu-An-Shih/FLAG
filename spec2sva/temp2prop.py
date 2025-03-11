from itertools import product
import sys
from typing import Callable

#from spec2sva.utils.ast2concrete import ast2concrete
import spec2sva.utils.ast2concrete as ast2concrete

class Temp2Prop:

    def __init__(self, signals: list, templates: list):
        ### Initialize the Temp2Prop object ###

        self._signals = []
        self._words = []
        for signal in signals:
            if signal['type'] == 'signal':
                self._signals.append(signal['name'])
            elif signal['type'] == 'word':
                self._words.append(tuple([signal['name'], signal['width']]))

        self._templates = templates

        # Generate the properties
        self._properties = []
        self._run()


    def _check_communicative_order(self, ast: dict, operator: str, comparator: Callable[[str, str], bool]) -> bool:
        ### Check if the template/property maintains the communicative order of the operators ###

        if ast['type'] == 'basic':
            return True
        else:
            assert ast['type'] == 'operator'
            
            if ast['operator'] == operator:
                # NOTE: Assume there are no nested operators of the same type
                operand_list = [ast2concrete.ast_to_ltl(operand) for operand in ast['operands']]
                if not all(comparator(operand_list[i], operand_list[i+1]) for i in range(len(operand_list)-1)):
                    return False
            
            for operand in ast['operands']:
                if self._check_communicative_order(operand, operator, comparator) == False:
                    return False
            
            return True


    def _substitute(self, phrase: dict) -> list:
        ### Substitute the signal values into the template and return properties ###
        # WARNING: This function should be modified or extended if new operators are added to the grammar

        new_phrases = []
        if phrase['type'] == 'basic':
            vartype = phrase['operands'][0]['variable']
            assert vartype in ['signal', 'word', 'signal/word']

            # NOTE: Python 3.10+ is required for the match-case syntax
            match phrase['operator']:
                case '==' | '!=':
                    # NOTE: 'sig != 0' is same as 'sig == 1' -- Only use '==' for signals to avoid redundancy
                    if phrase['operator'] == '!=':
                        assert vartype == 'word'
                    if vartype == 'signal' or vartype == 'signal/word':
                        for signal in self._signals:
                            new_phrases += [{'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': signal}, {'type': 'variable', 'variable': str(i)}]} for i in [0, 1]]
                    if vartype == 'word' or vartype == 'signal/word':
                        for word, width in self._words:
                            # NOTE: This might generate too many properties for wide words. Should we constraint this?
                            new_phrases += [{'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': word}, {'type': 'variable', 'variable': str(i)}]} for i in range(2**width)]
                case '$rose' | '$fell':
                    assert vartype == 'signal'
                    for signal in self._signals:
                        new_phrases.append({'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': signal}]})
                case '$roseorfell':
                    assert vartype == 'signal'
                    for signal in self._signals:
                        new_phrases += [{'type': 'basic', 'operator': '$rose', 'operands': [{'type': 'variable', 'variable': signal}]}, {'type': 'basic', 'operator': '$fell', 'operands': [{'type': 'variable', 'variable': signal}]}]
                case '$stable':
                    if vartype == 'signal' or vartype == 'signal/word':
                        for signal in self._signals:
                            new_phrases.append({'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': signal}]})
                    if vartype == 'word' or vartype == 'signal/word':
                        for word, _ in self._words:
                            new_phrases.append({'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': word}]})
                case _:
                    raise ValueError(f"Unknown operator: {phrase['operator']}")
        elif phrase['type'] == 'operator':
            # Get the expanded subphrases by substituting each operand
            subphrases_list = []
            for operand in phrase['operands']:
                subphrases_list.append(self._substitute(operand))
            # Enumerate all combinations of the expanded subphrases
            operand_combinations = list(product(*subphrases_list))
            # Avoid generating invalid combinations for commutative operators
            if phrase['operator'] == 'And' or phrase['operator'] == 'Or':
                #dict_lookup = {ast2concrete.ast_to_ltl(ast): ast for lst in subphrases_list for ast in lst}
                ltl_combs = [tuple(ast2concrete.ast_to_ltl(ast) for ast in comb) for comb in operand_combinations]
                
                # Remove combinations with repeated operands
                ltl_combs = [comb for comb in ltl_combs if len(set(comb)) == len(comb)]
                # Remove combinations with the same operands in a different order
                ltl_combs = set(tuple(sorted(comb)) for comb in ltl_combs)
                
                operand_combinations = [tuple(ast2concrete.ltl_to_ast(ltl) for ltl in comb) for comb in sorted(ltl_combs)]
            
            # Expand the operator with each combination of operands
            for new_operands in operand_combinations:
                new_phrases.append({'type': 'operator', 'operator': phrase['operator'], 'operands': list(new_operands)})
        else:
            raise ValueError(f"Invalid phrase type: {phrase['type']}")

        return new_phrases
    
    def _run(self):
        ### Generate the properties ###

        # Remove duplicate templates
        # valid_templates = []
        # for template in self._templates:
        #     if self._check_communicative_order(template['ast'], 'Or', lambda x, y: x <= y) and self._check_communicative_order(template['ast'], 'And', lambda x, y: x <= y):
        #         valid_templates.append(template)
        # self._templates = valid_templates
        
        # Generate properties from templates
        properties = []
        for template in self._templates:
            properties += self._substitute(template['ast'])
        
        for property in properties:
            self._properties.append({'nl': ast2concrete.ast_to_nl(property), 'ltl': ast2concrete.ast_to_ltl(property), 'ast': property})
        
        # Remove duplicate properties
        # valid_properties = []
        # for property in self._properties:
        #     if self._check_communicative_order(property['ast'], 'Or', lambda x, y: x < y) and self._check_communicative_order(property['ast'], 'And', lambda x, y: x < y):
        #         valid_properties.append(property)
        # self._properties = valid_properties


    def getTemplates_LTL(self) -> list:
        ### Return the generated templates in LTL format ###

        return [template['ltl'] for template in self._templates]
    
    def getProperties_LTL(self) -> list:
        ### Return the generated properties in LTL format ###

        return [property['ltl'] for property in self._properties]
    
    def getProperties_NL(self) -> list:
        ### Return the generated properties in NL format ###

        return [property['nl'] for property in self._properties]
    
    def getProperties(self) -> list:
        ### Return the generated properties ###

        return self._properties
    