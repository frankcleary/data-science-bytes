Title: How to quickly test if an element belongs to a group
Date: 11-05-2014
Category: Tips
Tags: Code, Data, Python

One common pattern in data science and programming in general is needed to test if a given variable `x` belongs to a specific group. The group may be [stop words]({filename}filter-common-words.md) or a list of counties that are net exporters of apricots.

If the elements of the group exist in a list structure named `group` in python, it's easy enough to test membership with `if x in group`. Here's a performance test, where `word_list` is a list of all English words.

    :::python
    document = ['the', 'data', 'noob', 'element', 'starcraft']
    for word in document:
        if word in word_list:
            print '{} is a word'.format(word)
        else:
            print '{} is NOT a word'.format(word)

This takes about 10.7 ms on my machine, ~2 ms per word. That means that if you want to look at even a small group of 10,000 words it's going to take a significant amount of time. How to solve this problem? The set data structure! Consider the following change to the above code, where I've changed `word_list` to `word_set`.

    :::python
    word_set = set(word_list)    

    # time this section
    document = ['the', 'data', 'noob', 'element', 'starcraft']
    for word in document:
        if word in word_set:
            print '{} is a word'.format(word)
        else:
            print '{} is NOT a word'.format(word)

On my machine this now takes 645 *nano*seconds, roughly 15,000 times faster! The lesson is clear: if you want to test for membership in a group, use a set, not a list (or array).

To explain why the set is fast I'll use an analogy. Imagine you are given the task of determining if a family named Smith lives on a street (i.e. `'Smith' in street` in python terms). If the street is like a list, you have to visit every house and check the name on the mailbox. This process takes longer the more houses there are on the street, since you have to stop at every one. In contrast if the street is like a set the magic of sets lets you know the number of the house that the Smiths would live at if they live on the street and you need only check that one house. This way you only need to spend the time to check one house, no matter how long the street is.

If you're curious about the details check out this talk by Brandon Rhodes: [The Mighty Dictionary](http://pyvideo.org/video/276/the-mighty-dictionary-55).
