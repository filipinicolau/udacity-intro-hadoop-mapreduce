#!/usr/bin/python
"""
A MapReduce program that creates an index of all words that can be found in the
body of a forum post and node id they can be found in.

We do not include HTML markup in our index, nor strings that are not words (for
a somewhat loose definition of "word"), nor common words.

The MLStripper class and strip_tags method were written by Eloff
(http://stackoverflow.com/a/925630). The list of English stop words was taken
from http://norm.al/2009/04/14/list-of-english-stop-words/. The rest of the
code is my work.
"""

from __future__ import print_function
import sys
import csv
import re
from HTMLParser import HTMLParser

# I should probably use a library to get these stop words, or, at the least,
# store them externally.
STOP_WORDS = \
    ["a", "about", "above", "above", "across", "after", "afterwards", "again",
        "against", "all", "almost", "alone", "along", "already", "also",
        "although", "always", "am", "among", "amongst", "amoungst", "amount",
        "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway",
        "anywhere", "are", "around", "as", "at", "back", "be", "became",
        "because", "become", "becomes", "becoming", "been", "before",
        "beforehand", "behind", "being", "below", "beside", "besides",
        "between", "beyond", "bill", "both", "bottom", "but", "by", "call",
        "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de",
        "describe", "detail", "do", "done", "down", "due", "during", "each",
        "eg", "eight", "either", "eleven", "else", "elsewhere", "empty",
        "enough", "etc", "even", "ever", "every", "everyone", "everything",
        "everywhere", "except", "few", "fifteen", "fify", "fill", "find",
        "fire", "first", "five", "for", "former", "formerly", "forty", "found",
        "four", "from", "front", "full", "further", "get", "give", "go", "had",
        "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
        "hereby", "herein", "hereupon", "hers", "herself", "him", "himself",
        "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed",
        "interest", "into", "is", "it", "its", "itself", "keep", "last",
        "latter", "latterly", "least", "less", "ltd", "made", "many", "may",
        "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most",
        "mostly", "move", "much", "must", "my", "myself", "name", "namely",
        "neither", "never", "nevertheless", "next", "nine", "no", "nobody",
        "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off",
        "often", "on", "once", "one", "only", "onto", "or", "other", "others",
        "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part",
        "per", "perhaps", "please", "put", "rather", "re", "same", "see",
        "seem", "seemed", "seeming", "seems", "serious", "several", "she",
        "should", "show", "side", "since", "sincere", "six", "sixty", "so",
        "some", "somehow", "someone", "something", "sometime", "sometimes",
        "somewhere", "still", "such", "system", "take", "ten", "than", "that",
        "the", "their", "them", "themselves", "then", "thence", "there",
        "thereafter", "thereby", "therefore", "therein", "thereupon", "these",
        "they", "thickv", "thin", "third", "this", "those", "though", "three",
        "through", "throughout", "thru", "thus", "to", "together", "too", "top",
        "toward", "towards", "twelve", "twenty", "two", "un", "under", "until",
        "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what",
        "whatever", "when", "whence", "whenever", "where", "whereafter",
        "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
        "which", "while", "whither", "who", "whoever", "whole", "whom", "whose",
        "why", "will", "with", "within", "without", "would", "yet", "you",
        "your", "yours", "yourself", "yourselves", "the"]

class MLStripper(HTMLParser):
    """ From http://stackoverflow.com/a/925630 """
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        """ get data """
        return ''.join(self.fed)

def strip_tags(html):
    """ From http://stackoverflow.com/a/925630 """
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()

def error(*objs):
    """ Output error message to standard error. """
    print("ERROR: ", *objs, file=sys.stderr)

def mapper():
    """ MapReducer Mapper. """
    reader = csv.reader(sys.stdin, delimiter='\t')
    writer = \
        csv.writer(
            sys.stdout, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)

    # Skip header.
    reader.next()
    for line in reader:
        body = line[4]
        try:
            # Get rid of HTML tags.
            # May fail for weird characters.
            body = strip_tags(body)
        except UnicodeDecodeError as ex:
            error(ex)
            continue
        node_id = line[0]
        parts = re.split(r'\s|[.!?:;"()<>[\]#$=\-/,]', body)
        # Filter out common English words.
        parts = [w for w in parts if not w.lower() in STOP_WORDS]
        for part in parts:
            try:
                # Only accept words, not gobbledygook.
                # May fail for non-ASCII characters
                if re.match(r"^\w+$", part):
                    writer.writerow([part.lower(), 1, node_id])
            except UnicodeDecodeError as ex:
                error(ex)

if __name__ == "__main__":
    mapper()

