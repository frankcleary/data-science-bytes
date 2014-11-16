"""
Related posts plugin for Pelican
================================

Adds related_posts variable to article's context
"""

from pelican import signals
from gensim import corpora, models, similarities
import os
import nltk
from collections import defaultdict
from pprint import pprint

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
    fname_scores = defaultdict(list)
    for fname, sims in zip(fnames, index):
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        for id, score in sims:
            if fname == fnames[id]:
                continue
            fname_scores[os.path.abspath(fname)].append(
                (os.path.abspath(fnames[id]), score)
            )
    return fname_scores


def add_related_posts(generator):
    # get the max number of entries from settings
    # or fall back to default (5)
    fname_scores = recommend_articles()
    numentries = 5
    articles_by_path = {art.source_path: art for art in generator.articles}
    for article in generator.articles:
        article.score = {}
    for article in generator.articles:
        article.score = {}
        related_posts = sorted(fname_scores[article.source_path], key=lambda x: -x[1])
        related_posts = filter(lambda x: 'pages' not in x[0], related_posts)
        print(article)
        pprint(related_posts)
        posts = []
        for i, entry in enumerate(related_posts):
            #if i >= numentries:
            #    break
            source_path, similarity = entry
            try:
                art = articles_by_path[source_path]
                article.score[art.source_path] = similarity
            except KeyError:
                print "can't find article {}".format(source_path)
            posts.append(art)
        article.related_posts = posts

def register():
    signals.article_generator_finalized.connect(add_related_posts)