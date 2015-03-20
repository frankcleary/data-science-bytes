Title: Analyzing large xml files in python
Date: 3-19-2015
Category: Tips
Tags: python, data, xml, etree

To show some techniques for working with files that are too large to fit on memory, I'm writing this post on a 10 year old laptop with 512 Mb of RAM and a 1.2 GHz celeron processor. The data in question is an xml format [dump of data from stack overflow](https://archive.org/details/stackexchange), the uncompressed file would not fit on the disk of this machine so I'll work with the compressed files directly ([more on that here]({filename}/read-zipped-files.ipynb)).

# Reading xml without taking up a lot of memory

As [this article](http://effbot.org/elementtree/iterparse.htm) explains, extra care is needed when using python's xml.etree module to avoid loading too many references into memory. The key is to access the root element outside of the loop, then `clear()` it within the loop to avoid building up a tree. Here I read through the file and create a dictionary of dates to number of posts on that date, using pandas to output the data in csv format.

    :::python
    import bz2
    import pandas as pd

    from collections import defaultdict
    from xml.etree import cElementTree

    def parse_file(filename):
        """Count the number of posts on each day for stack exchange xml data"""
        date_counts = defaultdict(int)
        with bz2.BZ2File(filename) as f:
            iterparser = cElementTree.iterparse(f, events=('start', ))
            _, root = iterparser.next()
            for _, element in iterparser:
                if element.tag == 'row':
                    date_str = element.get('CreationDate', '').split('T')[0]
                    date_counts[date_str] += 1
                root.clear()
        return date_counts

    date_counts = parse_file('stackoverflow.com-Posts.bz2')
    date_counts_df = pd.DataFrame.from_dict(date_counts, orient='index')
    date_counts_df.columns = ['num_posts']
    date_counts_df.to_csv('stackex_by_date.csv')


<img src="/extra/images/python-xml.jpg" title="parsing xml on an inspiron 1200">
