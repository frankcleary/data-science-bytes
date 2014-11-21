Pelican plugin that finds articles about similar topics
=======================================================

Frank Cleary - www.datasciencebytes.com

This plugin uses the gensim library to find articles about similar topics to
each article in the site. The most similar articles up to a given limit
(default 5, can be specified in pelican configs as MAX_RELATED_POSTS) are added
in sorted order of similarity as a list to the related_posts attribute of the
article. The article also contains a dictionary of related article similarity
scores keyed by related_article.source_path.

The gensim library requires numpy and scipy, which may be non-trivial to
install.

Add the following (or similar) to the article template to show the results.
```html
{% if article.related_posts %}
<h1>Related Posts</h1>
  <ul>
    {% for related_post in article.related_posts %}
      <li><a href="{{ SITEURL }}/{{ related_post.url }}">{{ related_post.title }}</a>,
      Score: {{ '%0.3f' % article.score.get(related_post.source_path) }}</li>
    {% endfor %}
  </ul>
{% endif %}
```

Some parts of this implementation relating to pelican are based on:
https://github.com/getpelican/pelican-plugins/tree/master/related_posts