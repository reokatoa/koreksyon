from __future__ import print_function
import fileinput
import string
import re
import getopt
import sys
import operator
import codecs
from unidecode import unidecode
from nltk import word_tokenize, PunktWordTokenizer

from Soundex import Soundex
import StringDistance
import Clustering

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

SOUNDEX_LANGUAGE = 'kre'
SOUNDEX_PREFIX = 1
SOUNDEX_LENGTH = 4
LEVENSHTEIN_MAX = 2

INPUT_FILE = sys.stdin
OUTPUT_FILE = sys.stdout
SPELLCHECK_FILE = None

PRINT_CLUSTERS = False
PRINT_EDITS = False
PRINT_DIFFS = False

def main():
    print("Reading corpus and building word frequency table", file=sys.stderr)
    words = wordcount()
    clusters = {}
    
    soundex = Soundex.get(SOUNDEX_LANGUAGE)
    soundex.setLength(SOUNDEX_LENGTH)
    soundex.setPrefixLength(SOUNDEX_PREFIX)
    
    print("Grouping words by Soundex", file=sys.stderr)
    bySoundex = Clustering.CommonValueClustering(words.keys(), soundex.encode)
    print("Clustering by Levenshtein distance", file=sys.stderr)
    for name, members in bySoundex.items():
        clusters[name] = []
        for cluster in Clustering.SingleLinkageOrderedClustering(members, words, StringDistance.levenshtein, LEVENSHTEIN_MAX).values():
            clusters[name].append(cluster)

    output(words, clusters)
    
def output(words, clusters):
    if PRINT_CLUSTERS:
        printClusters(words, clusters)
    elif PRINT_EDITS:
        printEdits(words, clusters)
    elif PRINT_DIFFS:
        printDiffs(words, clusters)

def parseArgs(argv):
    global SOUNDEX_PREFIX, SOUNDEX_LENGTH, LEVENSHTEIN_MAX, \
        INPUT_FILE, SPELLCHECK_FILE, \
        PRINT_CLUSTERS, PRINT_EDITS, PRINT_DIFFS

    try:
        opts = getopt.getopt(argv, "p:l:n:d:i:tcefs:")[0]
    except getopt.GetoptError:
        print("Error getting arguments", file=sys.stderr)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-l':
            SOUNDEX_LANGUAGE = arg
        elif opt == '-p':
            SOUNDEX_PREFIX = int(float(arg))
        elif opt == '-n':
            SOUNDEX_LENGTH = int(float(arg))
        elif opt == '-d':
            LEVENSHTEIN_MAX = int(float(arg))
        elif opt == '-i':
            INPUT_FILE = arg
        elif opt == '-s':
            SPELLCHECK_FILE = arg
        elif opt == '-e':
            PRINT_EDITS = True
        elif opt == '-c':
            PRINT_CLUSTERS = True
        elif opt == '-f':
            PRINT_DIFFS = True
        else:
            print("Unknown option", opt, file=sys.stderr)
            sys.exit(2)

def wordcount():
    words = {}
    for line in codecs.open(INPUT_FILE, 'r', 'utf-8'):
        line = re.sub("@[a-zA-Z0-9_]+", "", line)
        for word in PunktWordTokenizer().tokenize(line):
            w = cleanstring(word)
            if not w in words:
                words[w] = 0
            words[w] += 1
    return words

def printClusters(wordcount, clusters):
    accepted = {}
    if not SPELLCHECK_FILE is None:
        for line in codecs.open(SPELLCHECK_FILE, 'r', 'utf-8'):
            for word in PunktWordTokenizer().tokenize(line):
                accepted[cleanstring(word)] = 1

    for code, clusterSet in clusters.iteritems():
        for cluster in clusterSet:
            ct = 0
            for w in cluster:
                ct += wordcount[w]
            clusterwords = [(word+(u'*' if word in accepted else ''), wordcount[word]) for word in sorted(list(cluster), key=wordcount.get, reverse=True)]
            
            if len(cluster) > 1 and code[1] != '0': # Require at least two cluster members and a soundex code of more than one sound (assumes '0' is padding, not encoding)
                print(ct, code, [word for word in clusterwords if word[1]>2], sep='\t')

def printEdits(wordcount, clusters):
    editCounts = {}
    for clusterSet in clusters.values():
        for cluster in clusterSet:
            if len(cluster) > 1:
                ranked = sorted(list(cluster), key=wordcount.get, reverse=True)
                edits = StringDistance.levenshtein(ranked[0], ranked[1], path=True)
                for edit in edits[0]:
                    if not edit in editCounts:
                        editCounts[edit] = 0
                    editCounts[edit] += 1
    for edit, ct in editCounts.iteritems():
        print(edit, ct, sep='\t')            

def printDiffs(wordcount, clusters):
    diffCounts = {}
    for clusterSet in clusters.values():
        for cluster in clusterSet:
            if len(cluster) > 1:
                ranked = sorted(list(cluster), key=wordcount.get, reverse=True)
                diffs = StringDistance.pythonDiff(ranked[0], ranked[1], path=True)
                for diff in diffs:
                    if not diff in diffCounts:
                        diffCounts[diff] = 0
                    diffCounts[diff] += 1
    for diff, ct in diffCounts.iteritems():
        print(diff, ct, sep='\t')

def cleanstring(s):
    return s.lower().translate(dict((ord(char), None) for char in string.punctuation))

if __name__ == '__main__':
    parseArgs(sys.argv[1:])
    main()
