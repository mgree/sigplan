import json
import gensim
import sys, os, glob
import codecs

import nltk

use_wordnet = True
if use_wordnet:
    stemmer = nltk.stem.wordnet.WordNetLemmatizer()
    stem = stemmer.lemmatize
else:
    stemmer = nltk.stem.porter.PorterStemmer()
    stem = stemmer.stem

stops = set(map(lambda s: s.strip(),
                codecs.open("stopwords.dat","r","utf8").readlines()))

def tokenize(text):
    replacements = [("---"," "),
                    ("--"," "),
                    ("-", "")] # trying to capture multi-word keywords

    for (src,tgt) in replacements:
        text = text.replace(src,tgt)
    
    words = gensim.utils.simple_preprocess(text)

    return filter(lambda w: w not in stops, words)

def no_crlf(s):
    return ' '.join(s.split())

def parse(f):
    doc = json.loads(open(f).read())
    
    # if ('abs' not in doc): print file + " is missing an abstract"
    # if ('title' not in doc): print file + " is missing a title"

    conf = os.path.basename(os.path.dirname(f))
    title = doc.get('title',"").strip()
    authors = ' '.join(map(no_crlf, doc.get('authors',"")))
    meta = title + " - " + authors + " (" + conf + ")"
    return (meta.replace('"','\\"'),
            tokenize(title + " " + doc.get('abs',"")))

def load_docs(of,d):
    years = {}
    words = []

    doclist = codecs.open(of,"w","utf8")
                          
    for root in glob.glob(os.path.join(d,"*")):

        year = os.path.basename(root)
        years[year] = []
        
        for f in glob.glob(os.path.join(root,"*.txt")):
            title,doc = parse(f)

            doc = map(stem,doc)
            
            doclist.write(title + u'\n')
            
            for word in doc:
                if word not in words:
                    words.append(word)
            
            years[year].append(doc)

    doclist.close()
    return (years,words)

def words_to_dict(words):
    d = {}
    index = 0
    
    for word in words:
        d[word] = index
        index = index + 1

    return d

def docs_to_bow(years,d):
    bows = {}

    for year in years:
        bows[year] = []

        for doc in years[year]:
            bow = {}
            for word in doc:
                wordid = d[word]
                bow[wordid] = bow.get(wordid,0) + 1

            bows[year].append(bow)

    return bows

def as_dat(of, bows):
    out = open(of,"w")
    
    for year in bows:
        for bow in bows[year]:
            out.write(str(len(bow)))
            out.write(' ')
            for term in bow:
                out.write(str(term))
                out.write(':')
                out.write(str(bow[term]))
                out.write(' ')

            out.write('\n')

    out.close()

def as_vocab(of, words):
    out = codecs.open(of,"w","utf8")

    for word in words:
        out.write(word + u'\n')

    out.close()


def run(d,doc_file,dat_file,vocab_file):
    years,words = load_docs(doc_file, d)

    d = words_to_dict(words)
    bows = docs_to_bow(years,d)
    as_dat(dat_file,bows)
    as_vocab(vocab_file,words)

if __name__ == '__main__':
    args = dict(enumerate(sys.argv))
    d = args.get(1,"../scrape/main/")
    doc_file = args.get(2,"docs.dat")
    dat_file = args.get(3,"abstracts.dat")
    vocab_file = args.get(4,"vocab.dat")
    
    run(d,doc_file,dat_file,vocab_file)
