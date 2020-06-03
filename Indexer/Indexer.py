import os
import regex as re
import pickle
import math


def get_files(dir, suffix):
    """
    Returns all the files in a folder ending with suffix
    :param dir:
    :param suffix:
    :return: the list of file names
    """
    files = []
    for file in os.listdir(dir):
        if file.endswith(suffix):
            files.append(file)
    return files



def get_index(folder, documents):
    """
                     represent this index as a dictionary, keys: words, the values: the lists of positions
                     open text file and create its match_list
                     matches any character in the Latin unicode script
                     finditer returns an iterator
                     """
    index = dict()
    for document in documents:
        with open(os.path.join(folder, document), encoding="utf-8") as open_document:
            match_list = list(re.finditer("\p{L}+", open_document.read()))

        for match in match_list:
            match_word = match.group(0).lower()  # use group to access the iterator, 0 is the word
            # match.span() Return a tuple containing the (start, end) positions of the match
            #match.start() returns the start position
            match_pos = match.start(0)
            if match_word not in index:
                index[match_word] = dict()
            if document not in index[match_word]:
                index[match_word][document] = list()
            index[match_word][document].append(match_pos)

    pickle.dump(index, open('master_index.idx', "wb"))
    #dict = pickle.load( open( "save.p", "rb" ) )
    return index

def get_total_number_words_in(document):
    return len(re.findall('\p{L}+', open('Selma/' + document).read().lower()))

def term_frequency(term, document, document_number_words, index):
    """
    term frequency adjusted for document length : ft,d ÷ (number of words in d)
    """
    words = document_number_words[document]
    try:
        return len(index[term][document]) / words
    except:
        return 0


def inverse_document_frequency(term, documents, index):
    """
    an inverse document frequency factor is incorporated which diminishes the
    weight of terms that occur very frequently in the document set and increases the weight of terms that occur rarely.
    """
    document_count = 0
    for document in documents:
        try:
            index[term][document]
        except:
            continue
        document_count += 1
    if document_count == 0:
        return 0
    return math.log(len(documents) / (document_count), 10)


def tf_idf(documents, index):
    """
    tf–idf is the product of two statistics, term frequency and inverse document frequency.
    There are various ways for determining the exact values of both statistics.
    """
    tf_idf = dict()
    document_number_words = dict()

    for document in documents:
        document_number_words[document] = get_total_number_words_in(document)

    for document in documents:
        tf_idf[document] = dict()

    for term in index:
        for document in documents:
            tf_idf[document][term] = term_frequency(term, document, document_number_words,
                                                    index) * inverse_document_frequency(term, documents, index)
    return tf_idf

def get_sim(document_1, document_2, tf_idf, index):
    """
    calculates the cosine similarity btween two documents
    """
    num = 0
    denom_1 = 0
    denom_2 = 0
    for term in index:
        num += tf_idf[document_1][term] * tf_idf[document_2][term]
        denom_1 += math.pow(tf_idf[document_1][term], 2)
        denom_2 += math.pow(tf_idf[document_2][term], 2)
    return num/(math.sqrt(denom_1)* math.sqrt(denom_2))


def cos_sim (documents, tf_idf, index):
    cos_sim = dict()
    for document_1 in documents:
        print(document_1 , end ="      ")
        cos_sim[document_1]= dict()
        for document_2 in documents:
            sim = get_sim(document_1, document_2, tf_idf, index)
            cos_sim[document_1][document_2] = sim
            print("%.5f" %sim , end ="       ")
        print("\n")
    return cos_sim

def compare(cos_sim, documents):
    """to find the max cos_sim (but not one) to identify the most similar documents
    """
    maxSim = 0
    for document_1 in documents:
       for document_2 in documents:
            if (document_1 != document_2) & (cos_sim[document_1][document_2] > maxSim):
                maxSim = cos_sim[document_1][document_2]
                docs = [document_1, document_2, cos_sim[document_1][document_2]]
    return docs


documents = get_files("Selma", "txt")
index = get_index('Selma', documents)
print(index['samlar'])
#print(index)
print(index['ände'])
tf_idf = tf_idf(documents, index)

print(tf_idf['bannlyst.txt']['nils'])
print(tf_idf['bannlyst.txt']['et'])
print(tf_idf['gosta.txt']['nils'])
print(tf_idf['gosta.txt']['et'])

print(tf_idf['herrgard.txt']['nils'])
print(tf_idf['herrgard.txt']['et'])
print(tf_idf['jerusalem.txt']['nils'])
print(tf_idf['jerusalem.txt']['et'])
print(tf_idf['nils.txt']['nils'])

#print a matrix
print("bannlyst.txt      gosta.txt    herrgard.txt      jerusalem.txt     kejsaren.txt      marbacka.txt      nils.txt          osynliga.txt      troll.txt         ")
cos_sim = cos_sim(documents, tf_idf, index)
#print(cos_sim)
similar_docs = compare(cos_sim, documents)
print(similar_docs)


