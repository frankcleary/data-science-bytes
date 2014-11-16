"""
Related posts plugin for Pelican
================================

Adds related_posts variable to article's context
"""

from pelican import signals
from collections import Counter
from gensim import corpora, models, similarities
import os
import nltk
import time

def get_md_files(base_path='../content'):
    walk = os.walk('content')
    for path, _, filenames in walk:
        for fname in filenames:
            if fname.endswith('.md'):
                yield os.path.join(path, fname)


def tokenize_files(fnames):
    for fname in fnames:
        with open(fname) as f:
            tokenized_lines = [nltk.word_tokenize(line.strip()) for line in f]
        yield sum(tokenized_lines, [])

def filter_dictionary(raw_dictionary,
                      stop_words=nltk.corpus.stopwords.words('english') + [':'],
                      min_count=2):
    stop_ids = [raw_dictionary.token2id[word] for word in stop_words
                if word in raw_dictionary]
    one_time_ids = [id for id, freq in raw_dictionary.dfs.iteritems()
                    if freq < min_count]
    raw_dictionary.filter_tokens(stop_ids + one_time_ids)
    raw_dictionary.compactify()

def recommend_articles():
    fnames = list(get_md_files())
    documents = list(tokenize_files(fnames))
    dictionary = corpora.Dictionary(documents)
    filter_dictionary(dictionary)
    corpus = [dictionary.doc2bow(doc) for doc in documents]
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=5)
    index = similarities.MatrixSimilarity(lsi[corpus])
    for fname, sims in zip(fnames, index):
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        for id, score in sims:
            if fname == fnames[id]:
                print "RESULTS FOR: " + fname
                continue
            print score, fnames[id]


def add_related_posts(generator):
    # get the max number of entries from settings
    # or fall back to default (5)
    recommend_articles()
    numentries = generator.settings.get('RELATED_POSTS_MAX', 5)
    for article in generator.articles:
        # set priority in case of forced related posts
        if hasattr(article,'related_posts'):
            # split slugs 
            related_posts = article.related_posts.split(',')
            posts = [] 
            # get related articles
            for slug in related_posts:
                i = 0
                for a in generator.articles:
                    if i >= numentries: # break in case there are max related psots
                        break
                    if a.slug == slug:
                        posts.append(a)
                        i += 1

            article.related_posts = posts
        else:
            # no tag, no relation
            if not hasattr(article, 'tags'):
                continue

            # score = number of common tags
            scores = Counter()
            for tag in article.tags:
                scores += Counter(generator.tags[tag])

            # remove itself
            scores.pop(article)

            article.related_posts = [other for other, count 
                in scores.most_common(numentries)]

def register():
    signals.article_generator_finalized.connect(add_related_posts)