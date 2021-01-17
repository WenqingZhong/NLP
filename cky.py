"""
COMS W4705 - Natural Language Processing - Fall B 2020
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        span={}
        for t in range(len(tokens)):
            temp=tuple([tokens[t]])
            basic=self.grammar.rhs_to_rules[temp]
            
            if len(basic)==0:
                #print("error: some word is not in the rule table")
                return False
            
            
            subdict={}
            for b in basic:
                subdict.update({b[0]:[tuple([str(tokens[t]),t,t+1])]})
            
            span.update({tuple([t,t+1]):subdict})
            
            if len(basic)==0:
                span.update({tuple([t,t+1]):[]})
        
        for length in range(2,len(tokens)+1):
            for i in range(0,len(tokens)-length+1):
                j=i+length
                subdict={}
                for k in range(i+1,j):
                    span1=tuple([i,k]) 
                    span2=tuple([k,j])
                    
                    tags1=span[span1]
                    tags2=span[span2]
                    
                    for t1 in tags1:
                        for t2 in tags2:
                            temp=tuple([t1,t2])
                            next_tags=self.grammar.rhs_to_rules[temp]
                            if len(next_tags)>0:
                                for n in next_tags:
                                    if n[0] in subdict:
                                        subdict[n[0]].append(tuple([tuple([t1,i,k]),tuple([t2,k,j])]))
                                    else:
                                        subdict.update({n[0]:[tuple([tuple([t1,i,k]),tuple([t2,k,j])])]})    
                
                span.update({tuple([i,j]):subdict})
                
        
        final_result=span[0,len(tokens)]
        test = not bool(final_result)
        if test ==False:
            
            return True
        else:
           
            return False 
                            
       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        
        if (self.is_in_language(tokens)==False):
            return {},{}
        
        table= {}
        probs = {}
        
        for t in range(0,len(tokens)):
           
            temp=tuple([str(tokens[t])])
            basic=self.grammar.rhs_to_rules[temp]
 
            subbasicdict={}
            subpbasicdict={}
            
            for b in basic:
               
                subbasicdict.update({b[0]:tuple([tuple([b[1][0],t,t+1]),tuple([b[1][0],t,t+1])])})
                subpbasicdict.update({b[0]:math.log2(b[2])})
                
            table.update({tuple([t,t+1]):subbasicdict})
            probs.update({tuple([t,t+1]):subpbasicdict})
        
        
        for length in range(2,len(tokens)+1):
            for i in range(0,len(tokens)-length+1):
                j=i+length
                subdict={}
                psubdict={}
                
                for k in range(i+1,j):
                    span1=tuple([i,k]) 
                    span2=tuple([k,j])
                              
                    tags1=table[span1]                                  
                    tags2=table[span2]
                                        
                    for t1 in tags1:
                        for t2 in tags2:
                            temp=tuple([t1,t2])
                            next_tags=self.grammar.rhs_to_rules[temp]
                            if len(next_tags)>0:
                                for n in next_tags:
                                    p=math.log(n[2])
                                    
                                    if n[0] in psubdict:
                                        newprob=p+probs[span1][t1]+probs[span2][t2]
                                        oldprob=psubdict[n[0]] 
                                        
                                        if newprob>oldprob:
                                            
                                            subdict[n[0]]=tuple([tuple([t1,i,k]),tuple([t2,k,j])])
                                            psubdict[n[0]]=newprob
                                    else:
                                        subdict.update({n[0]:tuple([tuple([t1,i,k]),tuple([t2,k,j])])})    
                                        psubdict.update({n[0]:p+probs[span1][t1]+probs[span2][t2]})
                
                table.update({tuple([i,j]):subdict})
                probs.update({tuple([i,j]):psubdict})
                               
        return table, probs


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
      
    if j==i+1:
        return tuple([nt,chart[i,j][nt][0][0]])
    else:
        root= chart[(i,j)][nt]
        tuple1=tuple([nt,get_tree(chart,root[0][1],root[0][2],root[0][0]),get_tree(chart,root[1][1],root[1][2],root[1][0])])
        return tuple1
        
    return None 
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        #print(grammar.lhs_to_rules['FLIGHTS'])
        #toks=['miami', 'flights','cleveland', 'from', 'to','.']
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        parser.is_in_language(toks)
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
        get_tree(table, 0, len(toks), grammar.startsymbol)

