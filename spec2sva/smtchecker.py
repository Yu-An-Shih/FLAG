import sys
from typing import Optional
from z3 import *

class SMTChecker:

    def __init__(self, waveform_info: dict, properties: list):
        ### Initialize the SMTCheck object ###
        
        self._signals = waveform_info['signals']
        self._waveforms = waveform_info['waveforms']
        self._properties = properties
        
        # Signals information
        self._sigwidths = {signal['name']: signal['width'] if 'width' in signal else 1 for signal in self._signals}
        
        self._solver = Solver()
        
        # Waveform information
        self._variables = dict()
        self._cycles = 0

        self._run()


    def _createVars(self, waveform: dict) -> None:
        ### Create waveform variables ###

        self._variables.clear()
        self._cycles = len(waveform['signals'][0]['values'])
        
        for signal in waveform['signals']:
            # Neglect unrelated signals
            if signal['name'] not in self._sigwidths:
                continue
            
            width = self._sigwidths[signal['name']]
            self._variables[signal['name']] = [ BitVec('%s_%s' % (signal['name'], t), width) for t in range(self._cycles) ]
        
        #print(self._variables)

    
    def _encodeWaveformConstraints(self, waveform: dict) -> None:
        ### Encode waveform constraints ###
    
        # TODO: Combine _createVars and _encodeWaveformConstraints?
        
        constants = dict()
        for signal in waveform['signals']:
            # Neglect unrelated signals
            if signal['name'] not in self._sigwidths:
                continue

            signame = signal['name']
            for cyc, value in enumerate(signal['values']):
                if isinstance(value, int):
                    # variable == value
                    self._solver.add(self._variables[signame][cyc] == value)
                elif value != 'X':
                    if value not in constants:
                        constants[value] = self._variables[signame][cyc]
                    else:
                        # var2 == var1
                        self._solver.add(self._variables[signame][cyc] == constants[value])
        
        #print(self._solver.assertions())


    def _encodeProp_localize(self, ast: dict, cyc: int) -> Optional[z3.BoolRef]:
        ### Encode property constraints by recursively transfering operators into SMT formulas ###
        ### Localize according to the waveform ###
        # WARNING: This function should be modified or extended if new operators are added to the grammar

        # Propositions (base cases)
        if ast['type'] == 'basic':
            signal = ast['operands'][0]['variable']
            if signal not in self._variables:
                # NOTE: Skip the property if it contains signals not in the waveform
                return None

            match ast['operator']:
                case '==':
                    #signal = ast['operands'][0]['variable']
                    value = int(ast['operands'][1]['variable'])
                    return self._variables[signal][cyc] == value
                case '!=':
                    #signal = ast['operands'][0]['variable']
                    value = int(ast['operands'][1]['variable'])
                    return self._variables[signal][cyc] != value
                case '$rose':
                    #signal = ast['operands'][0]['variable']
                    return And(self._variables[signal][cyc - 1] == 0, self._variables[signal][cyc] == 1) if cyc > 0 else None
                case '$fell':
                    #signal = ast['operands'][0]['variable']
                    return And(self._variables[signal][cyc - 1] == 1, self._variables[signal][cyc] == 0) if cyc > 0 else None
                case '$stable':
                    #signal = ast['operands'][0]['variable']
                    return self._variables[signal][cyc - 1] == self._variables[signal][cyc] if cyc > 0 else None
                case _:
                    raise ValueError(f"Unknown basic operator: {ast['operator']}")
        # Propositional and temporal operators
        elif ast['type'] == 'operator':
            match ast['operator']:
                case 'And':
                    operands = [self._encodeProp_localize(operand, cyc) for operand in ast['operands']]
                    return And(*operands) if all(op is not None for op in operands) else None
                case 'Or':
                    operands = [self._encodeProp_localize(operand, cyc) for operand in ast['operands']]
                    return Or(*operands) if all(op is not None for op in operands) else None
                case 'Implies':
                    antecedent = self._encodeProp_localize(ast['operands'][0], cyc)
                    consequent = self._encodeProp_localize(ast['operands'][1], cyc)
                    return Implies(antecedent, consequent) if antecedent is not None and consequent is not None else None
                case 'X':
                    if cyc == self._cycles - 1:
                        return None
                    else:
                        return self._encodeProp_localize(ast['operands'][0], cyc + 1)
                case 'F':
                    events = [event for t in range(cyc, self._cycles) if (event := self._encodeProp_localize(ast['operands'][0], t)) is not None]
                    return Or(events) if events else None
                case 'G':
                    assert cyc == 0
                    events = [event for t in range(self._cycles) if (event := self._encodeProp_localize(ast['operands'][0], t)) is not None]
                    return And(events) if events else None
                case _:
                    raise ValueError(f"Unknown propositional/temporal operator: {ast['operator']}")
        else:
            raise ValueError(f"Invalid AST type: {ast['type']}")


    def _removeTautologies(self) -> None:
        ### Remove tautologies from the property list ###

        # Create an unconstrained waveform
        unconstrained_signals = [{'name': signal['name'], 'values': ['X', 'X', 'X']} for signal in self._signals]
        waveform = {'name': 'unconstrained', 'signals': unconstrained_signals}

        # Create waverform variables
        self._createVars(waveform)

        # DON'T encode waveform constraints
        # self._encodeWaveformConstraints(waveform)

        non_tautologies = []
        for property in self._properties:
            # A property is a tauology iff it holds on any (a.k.a. unconstrained) waveform
            # A property holds on a waveform iff it's negation is unsatisfiable
            if Solver().check(Not(self._encodeProp_localize(property['ast'], 0))) != z3.unsat:
                non_tautologies.append(property)
        
        self._properties = non_tautologies

        print('Properties after removing tautologies:', len(self._properties))

        # with open('non_tautologies.json', 'w') as f:
        #     import json
        #     json.dump(self._properties, f, indent=4)
        # sys.exit(0)

    
    """
    def _removeDuplicates(self) -> None:
        ### Remove duplicate properties ###

        # Create an unconstrained waveform
        signals_new = []
        for signal in self._waveforms[0]['signals']:
            signal_new = signal.copy()
            signal_new['values'] = ['X', 'X', 'X']
            signals_new.append(signal_new)
        waveform = {'name': self._waveforms[0]['name'], 'signals': signals_new}

        # Create waverform variables
        self._createVars(waveform)

        # DON'T encode waveform constraints
        # self._encodeWaveformConstraints(waveform)
        
        unique_props = []
        for property in self._properties:
            unique = True
            for unique_prop in unique_props:
                # encode1 = self._encodeProp_localize(property['ast'], 0)
                # encode2 = self._encodeProp_localize(unique_prop['ast'], 0)
                # if Solver().check(Not(And(Implies(encode1, encode2), Implies(encode2, encode1)))) == z3.unsat:
                if Solver().check(self._encodeProp_localize(property['ast'], 0) != self._encodeProp_localize(unique_prop['ast'], 0)) == z3.unsat:
                    unique = False
                    break
            if unique:
                unique_props.append(property)
        
        self._properties = unique_props

        print('Properties after removing duplicates:', len(self._properties))

        # with open('unique.json', 'w') as f:
        #     import json
        #     json.dump(self._properties, f, indent=4)
        #sys.exit(0)
    """
    

    def _run(self):
        ### Run the SMT check to filter out invalid properties ###

        print('Initial properties:', len(self._properties))
        
        # Remove tautologies
        self._removeTautologies()
        
        # Check properties for each waveform
        for waveform in self._waveforms:
            # Create waveform variables
            self._createVars(waveform)

            # Encode waveform constraints
            self._encodeWaveformConstraints(waveform)

            properties_held = []
            for property in self._properties:

                prop_local = self._encodeProp_localize(property['ast'], 0)
                if prop_local is None:
                    # NOTE: We assume the property holds if there is no constraint that can be checked
                    #       Possible reason: the property contains signals not in the waveform
                    properties_held.append(property)
                else:
                    # Save the current stack size - Paired with pop() to remove property constraints later
                    self._solver.push()
                    # Encode (negation of) property constraints
                    self._solver.add(Not(prop_local))
                    # Check the property and update the property list
                    if self._solver.check() == z3.unsat:
                        properties_held.append(property)
                    # Remove (negation of) property constraints
                    self._solver.pop()
            
            self._properties = properties_held
            self._solver.reset()

            print(f'Properties held after waveform \'{waveform['name']}\':', len(self._properties))
        
        # Remove duplicates
        #self._removeDuplicates()


    def getProperties_LTL(self) -> list:
        ### Return the properties that hold for all waveforms in LTL format ###

        return [property['ltl'] for property in self._properties]
    
    def getProperties_NL(self) -> list:
        ### Return the properties that hold for all waveforms in NL format ###

        return [property['nl'] for property in self._properties]
    
    def getProperties(self) -> list:
        ### Return the properties that hold for all waveforms ###

        return self._properties
    