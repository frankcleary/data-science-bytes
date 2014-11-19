Title: Get a list of all English words in python
Date: 11-3-2014
Category: Tips
Tags: data, python, nltk

The `nltk` library for python contains a lot of useful data in addition to it's functions. One convient data set is a list of all english words, accessible like so:

    :::python
    from nltk.corpus import words
    word_list = words.words()
    # prints 236736
    print len(word_list)

You will probably first have to download the word list using `nltk`'s `download()` function. The following code should give you a GUI window to select the data you want (look for "words" under the "Corpora" tab):

    :::python
    import nltk
    nltk.download()
