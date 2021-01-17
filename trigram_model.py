import sys
from collections import defaultdict
import math
import random
import os
import os.path
"""
COMS W4705 - Natural Language Processing - Fall B 2020
Homework 1 - Programming Component: Trigram Language Models
Yassine Benajiba
"""

def corpus_reader(corpusfile, lexicon=None): 
    with open(corpusfile,'r') as corpus: 
        for line in corpus: 
            if line.strip():
                sequence = line.lower().strip().split()
                if lexicon: 
                    yield [word if word in lexicon else "UNK" for word in sequence]
                else: 
                    yield sequence

def get_lexicon(corpus):
    word_counts = defaultdict(int)
    for sentence in corpus:
        for word in sentence: 
            word_counts[word] += 1
    return set(word for word in word_counts if word_counts[word] > 1)  



def get_ngrams(sequence, n):
    """
    COMPLETE THIS FUNCTION (PART 1)
    Given a sequence, this function should return a list of n-grams, where each n-gram is a Python tuple.
    This should work for arbitrary values of 1 <= n < len(sequence).
    """
    
    ngrams=[]
    if n==1:
        t=tuple(['STRAT'])
        ngrams.append(t)
    else: 
        for k in range(1,n):
          if len(sequence)>=n-k:
            t1=tuple (['START']*k)
            t2=tuple(sequence[j] for j in range(0,n-k))          
            t= t1+t2
            ngrams.insert(0,t)
    
    for i in range(len(sequence)-n+1):
        t=tuple(sequence[j] for j in range(i,i+n))
        ngrams.append(t)
    
     
    end1=tuple(sequence[j] for j in range(len(sequence)-n+1,len(sequence)))
    end2=tuple(['STOP'])
    end=end1+end2
    ngrams.append(end)
    return ngrams


class TrigramModel(object):
    
    def __init__(self, corpusfile):
    
        # Iterate through the corpus once to build a lexicon 
        generator = corpus_reader(corpusfile)
        self.lexicon = get_lexicon(generator)
        self.lexicon.add("UNK")
        self.lexicon.add("START")
        self.lexicon.add("STOP")
    
        # Now iterate through the corpus again and count ngrams
        generator = corpus_reader(corpusfile, self.lexicon)
        self.count_ngrams(generator)
        

    def count_ngrams(self, corpus):
        """
        COMPLETE THIS METHOD (PART 2)
        Given a corpus iterator, populate dictionaries of unigram, bigram,
        and trigram counts. 
        """
   
        self.unigramcounts = {} # might want to use defaultdict or Counter instead
        self.bigramcounts = {} 
        self.trigramcounts = {} 
 
        ##Your code here
        self.totaluni=0
        
        
        
        for sentence in corpus:
            if len(sentence)>=1: 
                uni=get_ngrams(sentence, 1)  
                for u in uni:
                    if u not in self.unigramcounts:
                        self.unigramcounts.update({u:1})
                    else:
                        self.unigramcounts[u]=self.unigramcounts[u]+1
            if len(sentence)>=2: 
                bi=get_ngrams(sentence, 2)  
                for b in bi:                
                    if b not in self.bigramcounts:
                        self.bigramcounts.update({b:1})
                    else:
                        self.bigramcounts[b]=self.bigramcounts[b]+1
                        
            if len(sentence)>=3: 
                tri=get_ngrams(sentence, 3)
                for t in tri:                
                    if t not in self.trigramcounts:
                        self.trigramcounts.update({t:1})
                    else:
                        self.trigramcounts[t]=self.trigramcounts[t]+1
        
        self.totaluni=sum(self.unigramcounts.values())
        
        totalSTARTbi=0
        for b in self.bigramcounts:
            if b[0]=='START':
                totalSTARTbi += self.bigramcounts.get(b)
        
        self.totalSTART=totalSTARTbi
        
        
        return
    
    def raw_trigram_probability(self,trigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) trigram probability
        """
        
        tri=self.trigramcounts.get(trigram)
        if tri != None:
        
            bi=tuple([trigram[0]])+tuple([trigram[1]])
            
            if bi in self.bigramcounts:
                prob=tri/self.bigramcounts.get(bi)
            else: # when trigram is ['START', 'START','something']
                    prob=tri/self.totalSTART              
            return prob
        else:
            return 0
    
    def raw_bigram_probability(self, bigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) bigram probability
        """
        
        uni= tuple([bigram[0]])
        bi=self.bigramcounts.get(bigram)
        if bi != None:
            if uni in self.unigramcounts:
                prob=bi/self.unigramcounts.get(uni)
            else: #when bigram is ['START','something']
                prob=bi/self.totalSTART

            return prob
        else:
            return 0
       
        
    
    def raw_unigram_probability(self, unigram):
        """
        COMPLETE THIS METHOD (PART 3)
        Returns the raw (unsmoothed) unigram probability.
        """

        #hint: recomputing the denominator every time the method is called
        # can be slow! You might want to compute the total number of words once, 
        # store in the TrigramModel instance, and then re-use it. 
        uni=self.unigramcounts.get(unigram)
        if uni != None:
            prob=uni/self.totaluni
            return prob
        else:
            return 0

    def generate_sentence(self,t=20): 
        """
        COMPLETE THIS METHOD (OPTIONAL)
        Generate a random sentence from the trigram model. t specifies the
        max length, but the sentence may be shorter if STOP is reached.
        """
        return result            

    def smoothed_trigram_probability(self, trigram):
        """
        COMPLETE THIS METHOD (PART 4)
        Returns the smoothed trigram probability (using linear interpolation). 
        """
        lambda1 = 1/3.0
        lambda2 = 1/3.0
        lambda3 = 1/3.0
        
        unigram= tuple([trigram[2]])
        bigram=tuple([trigram[1]])+tuple([trigram[2]])
        
        rawtri =self.raw_trigram_probability(trigram)
        rawbi =self.raw_bigram_probability(bigram)
        rawuni =self.raw_unigram_probability(unigram)
        
        smooth=lambda1*rawtri+lambda2*rawbi+lambda3*rawuni
        
        return smooth
        
    def sentence_logprob(self, sentence):
        """
        COMPLETE THIS METHOD (PART 5)
        Returns the log probability of an entire sequence.
        """
        tri=get_ngrams(sentence, 3)
        Ps=0.0
        for t in tri:
            p=self.smoothed_trigram_probability(t)           
            logp= math.log2(p)
            Ps=Ps+logp
        return Ps
    

    def perplexity(self, corpus):
        """
        COMPLETE THIS METHOD (PART 6) 
        Returns the log probability of an entire sequence.
        """
        m = 0
        totalP=0.0
        for sentence in corpus:
            m = m+ len(sentence)+2  #'START' and 'STOP' 
            Ps=self.sentence_logprob(sentence)
            totalP += Ps
            
        l= totalP/m
        perp=2**(-l)
        
        return perp 


def essay_scoring_experiment(training_file1, training_file2, testdir1, testdir2):

        model1 = TrigramModel(training_file1)
        model2 = TrigramModel(training_file2)

        total = 0
        correct = 0       
 
        for f in os.listdir(testdir1):
            pp = model1.perplexity(corpus_reader(os.path.join(testdir1, f), model1.lexicon))
            # .. 
            
            pp2= model2.perplexity(corpus_reader(os.path.join(testdir1, f), model2.lexicon))
            
            total+=1
            if pp<pp2:
                correct+=1
    
        for f in os.listdir(testdir2):
            pp = model2.perplexity(corpus_reader(os.path.join(testdir2, f), model2.lexicon))
            # .. 
            pp2= model1.perplexity(corpus_reader(os.path.join(testdir2, f), model1.lexicon))
            
            total+=1
            if pp<pp2:
                correct+=1
        
        acc=correct/total
        
        return acc

if __name__ == "__main__":
     #model = TrigramModel(sys.argv[1]) 

    # put test code here...
    # or run the script from the command line with 
    # $ python -i trigram_model.py [corpus_file]
    # >>> 
    #
    # you can then call methods on the model instance in the interactive 
    # Python prompt. 

    
    # Testing perplexity: 
    # dev_corpus = corpus_reader(sys.argv[2], model.lexicon)
    # pp = model.perplexity(dev_corpus)
    # print(pp)


    # Essay scoring experiment: 
    acc = essay_scoring_experiment("train_high.txt", "train_low.txt", "test_high", "test_low")
    print(acc)
 
    
    