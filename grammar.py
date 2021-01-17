"""
COMS W4705 - Natural Language Processing - Fall B 2020
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""

import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file) 
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        # TODO, Part 1
        
        for l in self.lhs_to_rules:
            rules=self.lhs_to_rules[l]
            sumprob=0
            prob=[]
            for rule in rules:
                p=rule[2]
                rls=rule[1]
                lenrls=len(rls)
                if (lenrls==1):
                    if (rls[0].isupper()==True):
                        print(rule,rls)
                        print("error: terminal can only be lowercase!")
                        return False
                elif (lenrls==2):
                    if (rls[0].isupper()==False or rls[1].isupper()==False):
                        print("error: nonterminal can only be uppercase!")
                        return False
                else:
                    print("error: not in CNF format!")
                    return False
                
                prob.append(p)
                sumprob=fsum(prob)
            if (sumprob<0.999 or sumprob>1.001):
                print("error: probability doesn't sum to 1")
                return False   
        
        return True 


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)       
        grammar.verify_grammar()
