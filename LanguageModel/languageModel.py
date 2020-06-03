
"""
Concordance program to find all the concordances
of a pattern surrounded by width characters.
Usage: python concord.py file pattern width
"""
__author__ = "Pierre Nugues"
import regex as re
import sys
import math

def concord():
    file_name = "Selma.txt"
    pattern = "Nils"
    width = 10
    try:
        file = open(file_name, encoding="utf-8")
    except:
        print("Could not open file", file_name)
        exit(0)
    text = file.read()
    # spaces match tabs and newlines
    pattern = re.sub(' ', '\\s+', pattern)
    text = re.sub('\s+', ' ', text)  # Uncomment this to match/print newlines as spaces
    # pattern = '(.{0,25}Achaeans(?=(.{0,25})))'
    pattern = '(.{{0,{width}}}{pattern}(?=(.{{0,{width}}})))'.format(pattern=pattern, width=width)
    for match in re.finditer(pattern, text):
        print(match.group(1), match.group(2))
    # print the string with 0..width characters on either side

def tokenize4(text):
    """uses the punctuation and symbols to break the text into words
    returns a list of words"""
    spaced_tokens = re.sub('([\p{S}\p{P}])', r' \1 ', text)
    one_token_per_line = re.sub('\s+', '\n', spaced_tokens)
    tokens = one_token_per_line.split()
    return tokens

# def normalise(text):
#     sentences = re.split("(?<!Mr)(?<!Mrs)[\.\?!\”]\s+(?=[\p{Lu}])", text)
#     normalised = ""
#     for sentence in sentences:
#         sentence = re.sub("[[:punct:]]", "", sentence).lower()
#         normalised += "<s> {} </s>".format(sentence)
#     return normalised

def normalise(text):
    """
    uses period, white space and capital letter to split sentences.
    not accurate, as there are sentences ending with other punctuations like "?"
    """
    sentences = re.split('[\.\?\!]\s*(?=[\p{P}]|[\p{Lu}])', text)
    normalized = ""
    for sentence in sentences:
        #sentence = re.sub("\r?\n|\r", "", sentence)
        sentence = re.sub("\s+", " ", sentence)
        sentence = re.sub("[\p{P}]", " ", sentence).lower() #remove the punctuation, change to lowercase
        normalized += "<s> {} </s>\n".format(sentence)
    return normalized

def tokenize(text):
    words = re.findall("\p{L}+", text)
    return words


def count_bigrams(words):
    bigrams = [tuple(words[inx:inx + 2])
               for inx in range(len(words) - 1)]
    frequencies = {}
    for bigram in bigrams:
        if bigram in frequencies:
            frequencies[bigram] += 1
        else:
            frequencies[bigram] = 1
    print(len(frequencies)) #number of bigrams
    return frequencies


def count_unigrams(words):
    frequency = {}
    for word in words:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    return frequency


def sentence_prob_uni(words, frequency_unigrams):
    sentences = {}
    current_prob = 1
    current_sentence = ""
    N = len(words)
    for word in words:
        if word == "</s>":
            sentences[current_sentence] = current_prob
            current_prob = 1
            current_sentence = ""
        elif not word == "<s>":
            current_prob *= frequency_unigrams[(word,)] / N
            current_sentence += " " + word
    return sentences


def sentence_prob_bi(words):
    unigram_freq = count_unigrams(words)
    bigram_freq = count_bigrams(words)
    sentences = {}
    current_prob = 1
    current_sentence = ""
    N = len(words)
    for i in range(N - 1):
        if words[i] == "</s>":
            sentences[current_sentence] = current_prob
            current_prob = 1
            current_sentence = ""
        ci = unigram_freq[words[i]]
        ciCi = bigram_freq[(words[i], words[i + 1])]
        p = ciCi / ci
        current_prob *= p
        current_sentence += words[i] + " "
    return sentences

import math


def bigrams(words, testWords):
    print("Bigram model")
    print("=============================================")
    print("wi wi+1 Ci,i+1 C(i) P(wi+1|wi)")
    print("=============================================")
    unigram_freq = count_unigrams(words)
    bigram_freq = count_bigrams(words)
    current_prob = 1
    entropy = 0
    current_sentence = ""
    sentences = {}
    N = len(testWords)
    for i in range(N):
        if testWords[i] == "</s>":
            current_sentence += testWords[i] + " "
            sentences[current_sentence] = current_prob
            print("Prob. bigrams: " + str(current_prob))
            geo_mean_prob = math.pow(current_prob, 1/(len(testWords)-1))
            print("Geometric mean prob: " + str(geo_mean_prob))
            entropy = math.log2(current_prob) * (-1 / (len(testWords)-1))
            print("Entropy rate: " + str(entropy))
            perplexity = math.pow(2, entropy)
            print("Perplexity " + str(perplexity)+"\n")
        ci = unigram_freq[testWords[i]]
        if not i == N - 1:
            nextWord = testWords[i + 1]
            try:
                ciCi = bigram_freq[(testWords[i], testWords[i + 1])]
                p = ciCi / ci
            except:
                ciCi = 0
                p = ci / len(words) #? different from the online answer

            current_prob *= p
            current_sentence += testWords[i] + " "
            print(testWords[i] + " " + str(nextWord) +
                  " " + str(ciCi) + " " + str(ci) + " " + str(p))

    return sentences

def unigrams(words, testWords):
    print("Unigram model")
    print("=============================================")
    print("wi C(wi) #words P(wi)")
    print("=============================================")
    unigram_freq = count_unigrams(words)
    bigram_freq = count_bigrams(words)
    current_prob = 1
    entropy = 0
    current_sentence = ""
    sentences = {}
    N = len(testWords)
    for i in range(1, N):
        ci = unigram_freq[testWords[i]]
        p = ci / len(words)
        current_prob *= p
        current_sentence += testWords[i] + " "
        print(testWords[i] + " " + str(ci) + " " + str(len(words)) + " " + str(p))
    current_sentence += testWords[i] + " "
    sentences[current_sentence] = current_prob
    print("Prob. Unigram: " + str(current_prob))
    geo_mean_prob = math.pow(current_prob, 1 / (len(testWords) - 1))
    print("Geometric mean prob: " + str(geo_mean_prob))
    entropy = math.log2(current_prob) * (-1 / (len(testWords)-1)) #minus 1 here because <s> is not included
    print("Entropy rate: " + str(entropy))
    perplexity = math.pow(2, entropy)
    print("Perplexity " + str(perplexity)+ "\n")

    return sentences


if __name__ == '__main__':
    text = open("Selma.txt", encoding="utf8").read()
    normalized_text = normalise(text)
    normalized_text = re.sub("\r?\n|\r", " ",  normalized_text)
    wordsList = re.split("\s+", normalized_text)
    wordsSet = set(wordsList)
    print(len(wordsSet))
    #f = open("normalized.txt", "a", encoding="utf8" )
    #f.write(normalized_text)

    testText = "Det var en gång en katt som hette Nils."
    testWords = normalise(testText)
    testWords = re.sub("\r?\n|\r", "", testWords)
    #print(testWords)
    testWordsList = re.split("\s+", testWords)
    #print(testWordsList)
    #unigrams(wordsList, testWordsList)
    bigrams(wordsList, testWordsList)
