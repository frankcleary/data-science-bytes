Title: Using topic modeling to find related blog posts
Date: 11-20-2014
Category: Tutorials
Tags: data, python, gensim, nltk, pelican, machine learning

Over the weekend I got curious about how different posts in this blog were 
similar to each other, and thought about putting links to similar posts at the 
end of each article. I used the [gensim](http://radimrehurek.com/gensim/) python library (topic modeling for humans) to find similar 
articles and I wrote a plugin for [pelican](http://docs.getpelican.com/), the 
blogging software that powers this site to insert links to the most similar 
articles.

The latent semantic indexing model that I chose to model topics uses the same 
ideas I discuss in my [SVD tutotial (finding similar research
papers)](http://www.frankcleary.com/svd), although the input features are scaled 
differently and a cosine distance metric is used. Since this is a data science 
blog I included the score of each similar article along with the link. The source code is below, also available on [github](https://github.com/frankcleary/DataScienceBytes/tree/master/similar_posts).

    :::python
    """
    Pelican plugin that finds articles about similar articles
    =========================================================
    Frank Cleary - www.datasciencebytes.com - frank@frankcleary.com
    
    This plugin uses the gensim library to find articles about similar topics to
    each article in the site. The most similar articles up to a given limit
    (default 5, can be specified in pelican configs as MAX_RELATED_POSTS) are added
    in sorted order of similarity as a list to the related_posts attribute of the
    article. The article also contains a dictionary of related article similarity
    scores keyed by related_article.source_path.
    
    The gensim library requires numpy and scipy, which may be non-trivial to
    install.
    
    Add the following (or similar) to the article template to show the results.
    {% if article.related_posts %}
    <h1>Related Posts</h1>
      <ul>
        {% for related_post in article.related_posts %}
          <li><a href="{{ SITEURL }}/{{ related_post.url }}">{{ related_post.title }}</a>,
          Score: {{ '%0.3f' % article.score.get(related_post.source_path) }}</li>
        {% endfor %}
      </ul>
    {% endif %}
    
    
    Some parts of this implementation relating to pelican are based on:
    https://github.com/getpelican/pelican-plugins/tree/master/related_posts
    """
    
    from collections import defaultdict
    
    # imports protected to fail gracefully
    imports = True
    try:
        from bs4 import BeautifulSoup
        import nltk
        from pelican import signals
        from gensim import corpora, models, similarities
    except ImportError as error:
        print "related_posts could not complete imports:"
        print error
        imports = False
    
    
    def filter_dictionary(raw_dictionary,
                          stop_words=nltk.corpus.stopwords.words('english'),
                          min_count=2):
        """Filter raw_dictionary inplace to remove stopwords and words occurring
        less than min_count number of times.
    
        Will compactify the dictionary before exiting.
    
        :param raw_dictionary: gensim.corpora.Dictionary to filter
        :param stop_words: iterable of words to remove
        :param min_count: int minimum word count in resulting dictionary
        """
        stop_ids = [raw_dictionary.token2id[word] for word in stop_words
                    if word in raw_dictionary.token2id]
        rare_ids = [id for id, freq in raw_dictionary.dfs.iteritems()
                    if freq < min_count]
        raw_dictionary.filter_tokens(stop_ids + rare_ids)
        raw_dictionary.compactify()
    
    
    def generate_similarity_index(documents, model=models.LsiModel  ):
        """Return gensim.MatrixSimilarity of text documents using the supplied
        model.
    
        :param documents: An iterable of documents consisting of a list of words
        :param model: gensim.models to apply
        :return: gensim.MatrixSimilary the similarity values for every document to
            every other document.
        """
        dictionary = corpora.Dictionary(documents)
        filter_dictionary(dictionary)
        corpus = [dictionary.doc2bow(doc) for doc in documents]
        topic_model = model(corpus, id2word=dictionary, num_topics=5)
        for topic in topic_model.print_topics():
            print topic
        return similarities.MatrixSimilarity(topic_model[corpus])
    
    
    def recommend_articles(articles, tokenizer=nltk.RegexpTokenizer(r'\w+')):
        """Return a dictionary keyed by article source_path whose values are a
        sorted (descending) list of (article.source_path, similarity_score) tuples
        for every other article.
    
        HTML tags are stripped.
    
        :param articles: articles from a pelican ArticleGenerator
        :param tokenizer: an nltk tokenizer used to split article text into words
        :return: dictionary of similarity scores of other articles to keyed article
        """
        article_texts = [BeautifulSoup(article.content).get_text().lower()
                         for article in articles]
        documents = [tokenizer.tokenize(text) for text in article_texts]
        index = generate_similarity_index(documents)
        similarity_scores = defaultdict(list)
        for article, sims in zip(articles, index):
            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            for id, score in sims:
                if article == articles[id]:
                    continue
                similarity_scores[article.source_path].append(
                    (articles[id].source_path, score)
                )
        return similarity_scores
    
    
    def add_related_posts(generator, default_max_related_posts=5):
        """Find articles related to each article in a pelican ArticleGenerator and
        add the source_paths of the related articles and their similarity scores to
        the article metadata.
    
        :param generator: a pelican ArticleGenerator
        :param default_max_related_posts: the default max number of most similar
         posts. This will be overridden if MAX_RELATED_POSTS is set in the pelican
         config file.
        """
        if not imports:
            return
        max_posts = generator.settings.get("MAX_RELATED_POSTS",
                                           default_max_related_posts)
        similarity_scores = recommend_articles(generator.articles)
        articles_by_path = {art.source_path: art for art in generator.articles}
        for article in generator.articles:
            related_posts = sorted(similarity_scores[article.source_path],
                                   key=lambda x: -x[1])
            article.related_posts = []
            article.score = {}
            for i, entry in enumerate(related_posts):
                if i >= max_posts:
                    break
                source_path, similarity = entry
                try:
                    related_post = articles_by_path[source_path]
                    article.score[unicode(related_post.source_path)] = similarity
                except KeyError:
                    print "can't find article {}".format(source_path)
                article.related_posts.append(related_post)
    
    
    def register():
        """Entry point for ArticleGenerator from pelican"""
        signals.article_generator_finalized.connect(add_related_posts)
