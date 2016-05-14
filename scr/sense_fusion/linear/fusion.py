#Non-Linear Version of Sense Fusion
import nlp_lib as nlp
import numpy as np
import scipy as sci

CSV_DIR = "../../csv/"
CSV_NAME = "R&G-65.csv"
VECTOR_DIR = "../test_vector/"
VECTOR_NAME = "100_3.vec"
VECTOR_DIM = 100

alpha = 1.0
beta = 1.0
gamma = 1.0
L_RATE  = 0.0001
L_STEP  = 0.0001
word_hypernyms = {}
word_hyponyms = {}
word_synonyms = {}
word_vectors = {}
word_senses = {}
word_pairs = {}
word_final_vectors = {}
word_sense_vectors = {}

word_sense_hyponyms = {}
word_sense_hypernyms = {}
word_sense_synonyms = {}
word_sense_vectors = {}
sense_hyponym_pooling = {}
sense_hypernym_pooling = {}
sense_synonym_pooling = {}

#sense_vectors = {}
vocab = []
def test_sense_vectors():
    human_score = []
    machine_score = []

    #Our old approach
    for w_pair in word_pairs:
        w1 = w_pair[0].lower()
        w2 = w_pair[1].lower()
        h_score = float(w_pair[2])

        v1 = word_final_vectors[w1]
        v2 = word_final_vectors[w2]
        m_score = np.dot(v1, np.transpose(v2) ) / ( np.linalg.norm(v1) * np.linalg.norm(v2) )
        
        human_score.append(h_score)
        machine_score.append(m_score)

    sp1_val, sp1_rel = sci.stats.spearmanr(human_score, machine_score)

    print "Our pooling approach Spearman rel", sp1_val

#    human_score = []
    machine_score = []

    #My Approach
    for w_pair in word_pairs:
        w1 = w_pair[0].lower()
        w2 = w_pair[1].lower()
        w1_s_vec = []
        w2_s_vec = []
        num_1 = 0
        m_score = 0.0
        for s in word_senses[w1]:
            if (word_sense_vectors.has_key(s) ):
                if ( np.linalg.norm(word_sense_vectors[s]) > 0 ): #not a zero vector
                    w1_s_vec.append( word_sense_vectors[s] )
                else:
                    print "WARNING, word",w,"sense",s,"zero"
        for s in word_senses[w2]:
            if (word_sense_vectors.has_key(s) ):
                if ( np.linalg.norm(word_sense_vectors[s]) > 0 ):#not a zero vec
                    w2_s_vec.append( word_sense_vectors[s] )
                else:
                    print "WARNING, word",w,"sense",s,"zero"
        for v1 in w1_s_vec:
            for v2 in w2_s_vec:
                m_score = m_score + np.dot(v1, np.transpose(v2) ) / ( np.linalg.norm(v1) * np.linalg.norm(v2) )

        m_score = m_score / ( len(w1_s_vec) * len(w2_s_vec) )
#        print m_score,w1,w2
        machine_score.append(m_score)

    print "machine_score",str( len(machine_score))
    print "human_score", str ( len(human_score))
    sp2_val, sp2_rel = sci.stats.spearmanr(human_score, machine_score)
    print "New Approach Spearman",sp2_val
def get_single_pooling_sense(s, word, rel_words):
    result = np.zeros(VECTOR_DIM)
    i = 1.0
    if (len(rel_words[s]) > 0 ):
        for w in rel_words[s]:
            if word_vectors.has_key(w):
                result = result + word_vectors[w]
                i = i + 1.0
    if ( ( i - 1.0 ) > 0.0 ):
        result = result / i
    return result
def get_full_pooling_sense(s, word):
    result = np.zeros(VECTOR_DIM)
    hyper_pool = np.zeros(VECTOR_DIM)
    hypon_pool = np.zeros(VECTOR_DIM)
    syn_pool = np.zeros(VECTOR_DIM)

    i = 1.0
    if (len(word_sense_hypernyms[s]) > 0):
        for hyper in word_sense_hypernyms[s]:
            if word_vectors.has_key(hyper):
                hyper_pool = hyper_pool + word_vectors[hyper]
                i = i + 1.0
    if ( ( i - 1.0 ) > 0.0 ):
        hyper_pool = hyper_pool / i

    i = 1.0
    if (len(word_sense_hyponyms[s]) > 0 ):
        for hypon in word_sense_hyponyms[s]:
            if word_vectors.has_key(hypon):
                hypon_pool = hypon_pool + word_vectors[hypon] 
                i = i + 1.0
    if ( ( i - 1.0 ) > 0.0 ):
        hypon_pool = hypon_pool / i

    i = 1.0
    if (len(word_sense_synonyms[s] ) > 0 ):
        for syn in word_sense_synonyms[s]:
            if word_vectors.has_key(syn):
                syn_pool = syn_pool + word_vectors[syn]
                i = i + 1.0
    if ( ( i - 1.0 ) > 0.0 ):
        syn_pool = syn_pool / i

    result = syn_pool + hypon_pool + hyper_pool
#    if ( word_vectors.has_key(word) ):
#    result = result + word_vectors[word]
    return result
def get_pooling(word):    
    if ( word_vectors.has_key(word) ):
        result = word_vectors[word]
    else:
        result = np.zeros(VECTOR_DIM)
    
    i = 0.0
    hyper_pool = np.zeros(VECTOR_DIM)
    for hyper in word_hypernyms[word]:
        if (word_vectors.has_key(hyper)):
            hyper_pool = hyper_pool + word_vectors[hyper]
            i = i + 1.0
    if (( i - 1.0 ) > 0.0):
        hyper_pool = hyper_pool / i
    result = result + hyper_pool

    j = 0.0
    hypon_pool = np.zeros(VECTOR_DIM)
    for hypon in word_hyponyms[word]:
        if (word_vectors.has_key(hypon)):
            hypon_pool = hypon_pool + word_vectors[hypon]
            j = j + 1.0
    if (( j -1.0 ) > 0.0 ):
        hypon_pool = hypon_pool / j
    result = result + hypon_pool

    k = 0.0
    synonym_pool = np.zeros(VECTOR_DIM)
    for synonym in word_synonyms[word]:
        if (word_vectors.has_key(synonym) ):
            synonym_pool = synonym_pool + word_vectors[synonym]
            k = k + 1.0
    if ( (k-1.0) > 0.0):
        synonym_pool = synonym_pool / k
    result = result + synonym_pool
    return result
def cost_function(word_pool_vector, sense_vector):
    result = np.linalg.norm( word_pool_vector - sense_vector)
    result = result * result * 0.5
    return result
if __name__ == "__main__":
    word_vectors = nlp.read_word_vectors(VECTOR_DIR + VECTOR_NAME)
    while ( L_RATE < 1.0):
        print "LEARNING_RATE", L_RATE
        word_pairs = nlp.read_csv(CSV_DIR + CSV_NAME)
        vocab = []
        for p in word_pairs:
            vocab.append(p[0])
            vocab.append(p[1])
        vocab = list(set(vocab))
        for w in vocab:
            word_hypernyms[w] = nlp.read_hypernyms(w)
            word_hyponyms[w] = nlp.read_hyponyms(w)
            word_synonyms[w] = nlp.read_synonyms(w)
            word_senses[w] = nlp.read_senses(w)
            for s in word_senses[w]:
                word_sense_hypernyms[s] = nlp.read_hypernyms_by_sense(s)
                word_sense_hyponyms[s] = nlp.read_hyponyms_by_sense(s)
                word_sense_synonyms[s] = nlp.read_synonyms_by_sense(s)
                word_sense_vectors[s] = get_full_pooling_sense(s,w)
                sense_hyponym_pooling[s] = get_single_pooling_sense(s, w, word_sense_hyponyms)
                sense_hypernym_pooling[s] = get_single_pooling_sense(s, w, word_sense_hypernyms)
                sense_synonym_pooling[s] = get_single_pooling_sense(s, w, word_sense_synonyms)
                word_sense_vectors[s] = get_full_pooling_sense(s, w)
            word_final_vectors[w] = get_pooling(w)

        for w in vocab:
            cost_val = 0.0
            sense_num = len(word_senses[w])
            weight_vec = np.ones(sense_num)
            mat_s_vectors = []
            simulate_w_vector = np.zeros(VECTOR_DIM)
            for s in word_senses[w]:
                mat_s_vectors.append(word_sense_vectors[s])
            mat_s_vectors = np.asarray(mat_s_vectors)
            simulate_w_vector = np.dot(weight_vec, mat_s_vectors)
            loss = cost_function(word_final_vectors[w], simulate_w_vector)
            pre_loss = loss
#            print "Word",w
#            print "Loss",loss
            iteration = 0
            LEARNING_RATE = L_RATE
            while ( (loss > 0.0) and iteration < 20):
                i = 0
                while ( i < len(weight_vec) ):
                    weight_vec[i] = weight_vec[i] - LEARNING_RATE * np.dot( (word_final_vectors[w] - simulate_w_vector)  , np.transpose(-mat_s_vectors[i] ) )
                    i = i + 1
                simulate_w_vector = np.dot(weight_vec, mat_s_vectors)
                loss = cost_function(word_final_vectors[w], simulate_w_vector)
                if ( loss < pre_loss ):
                    LEARNING_RATE = LEARNING_RATE / ( 1 + 0.001 )
#                print "word",w
#                print "loss",loss
                iteration = iteration + 1
            i = 0
            for s in word_senses[w]:
                word_sense_vectors[s] = weight_vec[i] * word_sense_vectors[s]
                i = i + 1
#                print "Word",w,"Sense",s,"vector",word_sense_vectors[s]
#                print "Weight",weight_vec
#        word_sense_vectors = sense_vectors
        #OK,calc Spearman
        test_sense_vectors()
        L_RATE = L_RATE + L_STEP
