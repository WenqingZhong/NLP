from conll_reader import DependencyStructure, DependencyEdge, conll_reader
from collections import defaultdict
import copy
import sys

import numpy as np
import keras

from extract_training_data import FeatureExtractor, State

class Parser(object): 

    def __init__(self, extractor, modelfile):
        self.model = keras.models.load_model(modelfile)
        self.extractor = extractor
        
        # The following dictionary from indices to output actions will be useful
        self.output_labels = dict([(index, action) for (action, index) in extractor.output_labels.items()])

    def parse_sentence(self, words, pos):
        state = State(range(1,len(words)))
        state.stack.append(0)    

        while state.buffer: 
            pass
            # TODO: Write the body of this loop for part 4 
            feature=self.extractor.get_input_representation(words, pos, state)            
            feature=feature.reshape(1, feature.shape[0])
            score=self.model.predict(feature)
            
            actions={}
            for i in range(len(score[0])):
                if score[0][i]>0:                   
                    actions.update({i:score[0][i]})
            
            sort_actions={k: v for k, v in sorted(actions.items(), key=lambda item: item[1],reverse=True)}          
            
            for a in sort_actions:
                
                real_actions=self.output_labels[a]             
                
                if ('arc' in real_actions[0] and len(state.stack)==0):
                    
                    continue
                elif ( real_actions[0]=='shift' and len(state.buffer)==1 and len(state.stack)>0):
                    
                    continue
                elif(real_actions[0]=='left_arc' and state.stack[-1]==0):
                    
                    continue
                else:
                    if (real_actions[0]=='shift'):
                        
                        state.shift()
                        break
                    elif(real_actions[0]=='left_arc'):
                        
                        state.left_arc(real_actions[1])
                        break
                    elif(real_actions[0]=='right_arc'):
                        
                        state.right_arc(real_actions[1])
                        break
                    else:
                        print("something is wroooooooong")
                    break
                                
              
        result = DependencyStructure()
        for p,c,r in state.deps: 
            result.add_deprel(DependencyEdge(c,words[c],pos[c],p, r))
        return result 
        

if __name__ == "__main__":

    WORD_VOCAB_FILE = 'data/words.vocab'
    POS_VOCAB_FILE = 'data/pos.vocab'

    try:
        word_vocab_f = open(WORD_VOCAB_FILE,'r')
        pos_vocab_f = open(POS_VOCAB_FILE,'r') 
    except FileNotFoundError:
        print("Could not find vocabulary files {} and {}".format(WORD_VOCAB_FILE, POS_VOCAB_FILE))
        sys.exit(1) 

    extractor = FeatureExtractor(word_vocab_f, pos_vocab_f)
    parser = Parser(extractor, sys.argv[1])
    i=0
    with open(sys.argv[2],'r') as in_file: 
        for dtree in conll_reader(in_file):
            i=i+1
            print(i)
            words = dtree.words()
            pos = dtree.pos()
            deps = parser.parse_sentence(words, pos)
            print(deps.print_conll())
            print()
        
