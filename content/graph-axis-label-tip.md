Title: Label graph axes!
Date: 11-8-2014
Category: Tips
Tags: Data, Python, matplotlib, Code

[Download IPython notebook for this post]({filename}extra/ipynb/axeslabeltip.ipynb).

It's easy enough to make a plot using matplotlib. 

    :::python
    import matplotlib.pyplot as plt
    import numpy as np

    time_point_array = np.arange(0, 5, .1)
    y_value_array = np.exp(time_point_array)
     
    plt.plot(time_point_array, y_value_array)

![basic matplotlib plot]({filename}extra/images/axeslabelbase.png)

This plot however is not great data science. In fact it's poor data science and it happens all too often. By far the biggest problem is the lack of axis labels, no one (including yourself next week) is going to be able to get any information out of this plot without proper axis labels.

With just a few extra lines this plot can be made presentable. Note that it's easy to include LaTeX formatting in matplotlib plots.

    :::python
    plt.plot(time_point_array, y_value_array, lw=2)
    label_format_dict = dict(fontsize=20, fontweight='bold')
    tick_format_dict = dict(labelsize=16, direction='out', top='off', right='off', 
                            length=4, width=1)
    plt.ylabel("Click rate $\mu s^{-1}$", label_format_dict)
    plt.xlabel("Time (min after launch)", label_format_dict)
    plt.tick_params(**tick_format_dict)

![fixed matplotlib plot]({filename}extra/images/axeslabelfixed.png)

Note how much more readable and presentable the second graph is. It's not going to win any design awards but it could be put in an informal presentation as is. Some of these settings can also be configured in the [matplotlibrc file](http://matplotlib.org/users/customizing.html#customizing-matplotlib), or via [IPython configs](http://ipython.org/ipython-doc/dev/config/intro.html) but for portability and reproducibility I'd recommend getting them under version control along with the code that produces the plots.

[Download IPython notebook for this post]({filename}extra/ipynb/axeslabeltip.ipynb)