Title: How to quickly test if an element belongs to a group
Date: 11-05-2014
Category: Tutorials
Tags: Code, Data, Python

A common need in data science is to test if a some group of data contains a given value. One specific example would be to test if a word is a [stop word]({filename}filter-common-words.md).

## The slow way

If the elements of the group exist in a `list` named `group` in python, it's easy enough to test membership with `if x in group`. Here's a performance test, where `word_list` is a list of all English words.

    :::python
    document = ['the', 'data', 'noob', 'element', 'starcraft']
    # takes about 10 ms
    for word in document:
        if word in word_list:
            print '{} is a word'.format(word)
        else:
            print '{} is NOT a word'.format(word)

This takes about 10.7 ms on my machine, ~2 ms per word. That means that if you want to look at even a small group of 10,000 words it's going to take a significant amount of time. 

## The fast way

There is a much faster means to this end: the `set` data structure! Consider the following change to the above code, where I've changed `word_list` to a `set` named `word_set`.

    :::python
    word_set = set(word_list)    

    # takes about 0.0006 ms
    document = ['the', 'data', 'noob', 'element', 'starcraft']
    for word in document:
        if word in word_set:
            print '{} is a word'.format(word)
        else:
            print '{} is NOT a word'.format(word)

On my machine this now takes 645 *nano*seconds, roughly 16,000 times faster! The lesson is clear: if you want to test for membership in a group, use a `set`, not a `list` (or other array like structure).

## Explanation

Testing for membership in sets is fast because the entire set doesn't need to be scanned. Imagine you are given the task of determining if a family named Smith lives on a street (`'Smith' in street` in python terms). If the street is like a list you have to visit every house and check the name on the mailbox. This process takes longer the more houses exist on the street, since you have to stop at every one until you find a match. In contrast if the street is like a set you can use the magic of a hash function to know the number of the house that the Smiths would live at if they live on the street. Then you need only check that one house, no matter how long the street is.

If you're curious about the details check out this talk by Brandon Rhodes: [The Mighty Dictionary](http://pyvideo.org/video/276/the-mighty-dictionary-55).
