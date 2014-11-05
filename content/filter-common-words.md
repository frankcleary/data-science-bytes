Title: Filter common words from documents
Category: Tips
Date: 11-4-2014

Often when working with text documents it is useful to filter out words that occur frequently in all documents. These words, called stop words, don't give any special hint about the document's content. The [nltk (Natural Language Toolkit) library](http://www.nltk.org/index.html) for python includes a list of stop words for several languages. For example:

    :::python
    from nltk.corpus import stopwords
    stop_word_list = stopwords.words('english')

    #  to quickly test if a word is not a stop word, use a set:
    stop_word_set = set(stop_word_list)
    document = 'The data is strong in this one'
    for word in document.split():    
    	if word.lower() not in stop_word_set:
            print word
    # outputs: data, strong, one

You will probably first have to download the stop words using `nltk`'s `download()` function. The following code should give you a GUI window to select the data you want (look for stopwords under the "Corpora" tab):

    :::python
    import nltk
    nltk.download()

