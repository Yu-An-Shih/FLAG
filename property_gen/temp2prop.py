from itertools import product
import sys

sys.path.append('../util')
import ast2concrete

class Temp2Prop:

    def __init__(self, signals: list, templates: list):
        ### Initialize the Temp2Prop object ###

        self._signals = []
        self._buses = []
        for signal in signals:
            if signal['type'] == 'signal':
                self._signals.append(signal['name'])
            elif signal['type'] == 'bus':
                self._buses.append(tuple([signal['name'], signal['width']]))

        self._templates = templates

        # Generate the properties
        self._properties = []
        self._run()


    def _substitute(self, phrase: dict) -> list:
        ### Substitute the signal values into the template and return properties ###
        # WARNING: This function should be modified or extended if new operators are added to the grammar

        new_phrases = []
        if phrase['type'] == 'basic':
            match phrase['operator']:
                case '==' | '!=':
                    assert phrase['operands'][0]['variable'] == 'signal/bus' and phrase['operands'][1]['variable'] == 'level/value'
                    for signal in self._signals:
                        new_phrases += [{'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': signal}, {'type': 'variable', 'variable': str(i)}]} for i in [0, 1]]
                    for bus, width in self._buses:
                        new_phrases += [{'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': bus}, {'type': 'variable', 'variable': str(i)}]} for i in range(2**width)]
                case '$rose' | '$fell':
                    assert phrase['operands'][0]['variable'] == 'signal'
                    for signal in self._signals:
                        new_phrases.append({'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': signal}]})
                case '$stable':
                    assert phrase['operands'][0]['variable'] == 'signal/bus'
                    for signal in self._signals:
                        new_phrases.append({'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': signal}]})
                    for bus, width in self._buses:
                        new_phrases.append({'type': 'basic', 'operator': phrase['operator'], 'operands': [{'type': 'variable', 'variable': bus}]})
                case _:
                    raise ValueError(f"Unknown operator: {phrase['operator']}")
        elif phrase['type'] == 'operator':
            # Get the expanded subphrases by substituting each operand
            subphrases_list = []
            for operand in phrase['operands']:
                subphrases_list.append(self._substitute(operand))
            # Enumerate all combinations of the expanded subphrases
            operand_combinations = list(product(*subphrases_list))
            # Expand the operator with each combination of operands
            for new_operands in operand_combinations:
                new_phrases.append({'type': 'operator', 'operator': phrase['operator'], 'operands': list(new_operands)})
        else:
            raise ValueError(f"Invalid phrase type: {phrase['type']}")

        return new_phrases
    
    def _run(self):
        ### Generate the properties ###

        properties = []
        for template in self._templates:
            properties += self._substitute(template['ast'])
        
        for property in properties:
            self._properties.append({'nl': ast2concrete.ast_to_nl(property), 'ltl': ast2concrete.ast_to_ltl(property), 'ast': property})


    def getProperties_LTL(self) -> list:
        ### Return the generated properties in LTL format ###

        return [property['ltl'] for property in self._properties]
    
    def getProperties_NL(self) -> list:
        ### Return the generated properties in NL format ###

        return [property['nl'] for property in self._properties]
    
    def getProperties(self) -> list:
        ### Return the generated properties ###

        return self._properties
    