Title: First Look at AWS Machine Learning
Date: 2015-04-12
Category: Tutorials
Tags: data, AWS, machine learning

<style>img {display: block; border: 3px solid grey;}</style>

Amazon Web Services recently announced [Amazon Machine Learning](http://aws.amazon.com/machine-learning/), promising to make large scale machine learning more accessible to non-experts. I was curious to try out this service so I fed it some weather data from Oakland International Airport to see how well and how easily it could predict the maximum temperature on a day given the weather during the last 7 days. I downloaded [this data](/data/oak-data.csv) from the National Climatic Data Center [(data documentation)](http://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt).

For input into the machine learning model I transformed this data into a csv file where each row contains the readings from the previous week, as well as our target variable, the maximum temperature on that day (see Amazon's [data format specs](http://docs.aws.amazon.com/machine-learning/latest/dg/creating_datasources.html)). The code for this transformation is at the end of this article.

## Using Amazon Machine Learning

Here are the steps I took to create a machine learning model:

1. Upload data file to S3 ([S3 basics](http://docs.aws.amazon.com/AmazonS3/latest/gsg/GetStartedWithS3.html)).

1. Select Create New... -> Datasource and ML model
<img src="/extra/images/aws-ml/aws-ml1.png" title="new ML model">

1. Select the data from S3.
<img src="/extra/images/aws-ml/aws-ml2.png" title="Select data">

1. AWS then determines the schema of your data. If this was a real machine learning effort on my part I'd go through and make sure the schema was correct, [sometimes one bad data point can throw everything off]({filename}pandas-bad-join-tip.md).
<img src="/extra/images/aws-ml/aws-ml3.png" title="schema">

1. Identify your target variable (here the variable was helpfully named "target" in the input data). In this case AWS selected "Numerical regression" as the model type.
<img src="/extra/images/aws-ml/aws-ml4.png" title="Select target">

1. After a few more click throughs the model is trained. Even for this very small input data the model spent a few minutes in the "pending" state. I wonder if AWS is provisioning something like an EMR cluster to do the computations.
<img src="/extra/images/aws-ml/aws-ml5.png" title="Model training">

1. After training AWS will evaluate the model, which also takes some time.
<img src="/extra/images/aws-ml/aws-ml6.png" title="evaluation">

1. When complete the evaluation shows a green box with a reassuring message.
<img src="/extra/images/aws-ml/aws-ml7.png" title="evaluation">

1. Selecting "Explore model performance" yields a histogram of residuals with no less than **five** choices for bin size. With all these binsize options you can really go in depth. The [keynote presentation](https://www.youtube.com/watch?v=NZBBkaJqBd8&feature=youtu.be) introducing Amazon Machine Learning includes video of clicking the different bin sizes, it felt a little desperate.
<img src="/extra/images/aws-ml/aws-ml8.png" title="exploration">

1. Once the model is trained you can get predictions either by uploading a file (for batch predictions) or through an API (for real time).

## Thoughts

I can see Amazon Machine Learning being very useful to a lot of people, especially as it continues to evolve. The ability to somewhat blindly upload a lot of data and get predictions from it will open up new opportunities to incorporate machine learning into applications.

I was underwhelmed with the post-model analysis provided. It would have been nice to know which coefficients are significantly different from zero. Or the coefficients themselves for that matter. Since Amazon is charging per predication I can see why they keep those hidden. In general I think it will still be very important to have experts identify and engineer features and develop (and iterate on) models to achieve optimal machine learning results.

I find it interesting that Amazon charges $0.10 per 1000 predictions, which in this case requires multiplying and summing 70 numbers. That seems a little steep. The real advantage is that you can go from a big data file to predictions with a few clicks.

## Code to transform data into model input.

    :::python
    import pandas as pd
    import numpy as np

    oak = pd.read_csv('data/oak-data.csv',
                      na_values=[9999, -9999],
                      parse_dates=['DATE'])
    oak = oak.set_index('DATE')
    drop_cols = ['STATION', 'STATION_NAME', 'SNWD',
                 'SNOW', 'WDF2', 'WDF5']
    oak = oak.drop(drop_cols, axis=1)

    # convert to deg F
    for col in ['TMAX', 'TMIN']:
        oak[col] = oak[col].apply(lambda x: (x / 10.) * (9 / 5.) + 32)

    feature_dfs = []
    for i in xrange(1, 8):
        tmp = oak.shift(-i)
        tmp.columns = [col + ('-%s' % i) for col in oak.columns]
        feature_dfs.append(tmp)
    features = pd.concat(feature_dfs, axis=1)
    features['target'] = oak['TMAX']
    features.to_csv('data/features.csv')
