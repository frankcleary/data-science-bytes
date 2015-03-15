Title: IPython 3.0 released
Date: 3-15-2015
Category: News
Tags: python, ipython, data

[IPython 3.0](http://ipython.org/ipython-doc/3/whatsnew/version3.html) has been released, with notable changes to the IPython Notebook, which is now evolving into the language-agnostic [Project Jupyter](http://jupyter.org/).

I think some of the new `nbconvert` tools will be useful:

> * Added a .ipynb exporter to nbconvert. It can be used by passing --to notebook as a commandline argument to nbconvert.
> * New nbconvert preprocessor called ClearOutputPreprocessor. This clears the output from IPython notebooks.
> * New preprocessor for nbconvert that executes all the code cells in a notebook. To run a notebook and save its output in a new notebook:
>    ```ipython nbconvert InputNotebook --ExecutePreprocessor.enabled=True --to notebook --output Executed```
