from itertools import product
import sys

import spec2sva.utils.ast2concrete as ast2concrete

class Gram2Temp:

    def __init__(self, grammer: dict):
        ### Initialize the Gram2Temp object ###

        self._grammer = grammer

        # Generate the property templates
        self._templates = []
        self._run()

    """
    def _isRecursive(self, phrase: dict, cat_name: str) -> bool:
        ### Check if the phrase contains the category itself (recursive) ###
        
        if phrase['type'] == 'category' and phrase['category'] == cat_name:
            return True
        elif phrase['type'] == 'operator':
            for operand in phrase['operands']:
                if self._isRecursive(operand, cat_name):
                    return True
        return False
    """

    def _flatten_phrase(self, phrase: dict, base_cat_name: str, base_category: list) -> list:
        ### Flatten the phrase - If it contains the base category, replace the base category with its actual phrases, thus expanding the phrase ###

        new_phrases = []
        if phrase['type'] == 'category' and phrase['category'] == base_cat_name:
            # Base case 1
            new_phrases = base_category
        elif phrase['type'] == 'category' or phrase['type'] == 'basic':
            # Base case 2
            new_phrases = [phrase]
        elif phrase['type'] == 'operator':
            # TODO: Avoid getting invalid combinations of operands

            # Get the expanded subphrases by flattening each operand
            subphrases_list = []
            for operand in phrase['operands']:
                subphrases = self._flatten_phrase(operand, base_cat_name, base_category)
                subphrases_list.append(subphrases)
            # Enumerate all combinations of the expanded subphrases
            operand_combinations = list(product(*subphrases_list))
            # Expand the operator with each combination of operands
            for new_operands in operand_combinations:
                new_phrases.append({'type': 'operator', 'operator': phrase['operator'], 'operands': list(new_operands)})
        else:
            raise ValueError(f"Invalid phrase type: {phrase['type']}")

        return new_phrases
    

    def _flatten_category(self, category: list, base_cat_name: str, base_category: list) -> list:
        ### Flatten the category - Replace each appearance of the base category with its actual phrases ###

        category_new = []
        # "Flatten" each phrase if it contains the base category
        for phrase in category:
            new_phrases = self._flatten_phrase(phrase, base_cat_name, base_category)
            category_new += new_phrases
        
        return category_new


    """
    def _flatten_category_self(self, category: list, cat_name: str, depth: int) -> list:
        ### Flatten the category - Replace each appearance of the itself (recursively) with its actual phrases  ###

        while depth > 0:
            category = self._flatten_category(category, cat_name, category)
            depth -= 1
        
        # Remove all property templates with Recursive types
        category_new = []
        for phrase in category:
            if not self._isRecursive(phrase, cat_name):
                category_new.append(phrase)

        return category_new"
    """
    

    def _run(self):
        ### Generate templates based on the grammer ###
        
        grammer = self._grammer.copy()

        # Pop the "base" category from the grammer
        base_cat_name = list(grammer.keys())[0]
        base_category = grammer.pop(base_cat_name)
        while grammer:
            # "Flatten" the base category if it contains itself
            # if base_cat_name in self._depths:
            #     base_category = self._flatten_category_self(base_category, base_cat_name, self._depths[base_cat_name])
            
            # "Flatten" other categories if they contain the base category
            grammer_new = dict()
            for cat_name, category in grammer.items():
                grammer_new[cat_name] = self._flatten_category(category, base_cat_name, base_category)
            grammer = grammer_new

            # Pop the "base" category from the grammer
            base_cat_name = list(grammer.keys())[0]
            base_category = grammer.pop(base_cat_name)
        
        # Transfer the expanded grammer into property templates
        for template in base_category:
            self._templates.append({'nl': ast2concrete.ast_to_nl(template), 'ltl': ast2concrete.ast_to_ltl(template), 'ast': template})
    

    def getTemplates_LTL(self) -> list:
        ### Return the property templates in LTL format ###

        return [template['ltl'] for template in self._templates]
    

    def getTemplates_NL(self) -> list:
        ### Return the property templates in natural language format ###

        return [template['nl'] for template in self._templates]
    
    
    def getTemplates(self) -> list:
        ### Return the property templates ###

        return self._templates
    