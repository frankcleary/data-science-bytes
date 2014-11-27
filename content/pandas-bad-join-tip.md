Title: When pandas joins go wrong: check data types
Date: 11-27-2014
Category: Tips
Tags: pandas, python, data

Writing and debugging joins can be especially difficult when dealing with data living in text files. Consider trying to join the following two csv files on the city_id column.

	:::console
	$ cat city-names.csv
	city_id,city_name
	1,Dublin
	2,Pleasanton
	3,Millbrae
	4,Richmond

	$ cat city-populations.csv
	city_id,city_population
	1,52105
	2,74110
	3,22424
	4,107571
	Unknown,116768

## Loading the data
Read the data into pandas with `read_csv`:

	:::python
	In [1]: import pandas as pd

	In [2]: city_names_df = pd.read_csv('city-names.csv')

	In [3]: city_pop_df = pd.read_csv('city-populations.csv')

	In [4]: city_names_df
	Out[4]:
	   city_id   city_name
	0        1      Dublin
	1        2  Pleasanton
	2        3    Millbrae
	3        4    Richmond

	In [5]: city_pop_df
	Out[5]:
	   city_id  city_population
	0        1            52105
	1        2            74110
	2        3            22424
	3        4           107571
	4  Unknown           116768

### Attempting the join
If we attempt to join the two dataframes on their shared columns (city_id in this case), the result is empty, although we would expect ids 1-4 to match:

	:::python	
	In [6]: city_names_df.merge(city_pop_df)
	Out[6]:
	Empty DataFrame
	Columns: [city_id, city_name, city_population]
	Index: []

## What went wrong
What's going on? The problem is that the value "Unknown" in `city-populations.csv` forces the entire column to be parsed as strings, which then don't equate with the their matching values in `city-names.csv`. This can be seen by inspecting the data types of the dataframes.

	:::python
	In [7]: city_names_df.dtypes
	Out[7]:
	city_id       int64
	city_name    object
	dtype: object

	In [8]: city_pop_df.dtypes
	Out[8]:
	city_id            object
	city_population     int64
	dtype: object

Notice that the city_id column has type numeric (int64) in one dataframe and object in the other. Looking in more detail:

	:::python
	In [9]: city_names_df.ix[0, 'city_id']
	Out[9]: 1

	In [10]: type(city_names_df.ix[0, 'city_id'])
	Out[10]: numpy.int64

	In [11]: city_pop_df.ix[0, 'city_id']
	Out[11]: '1'

	In [12]: type(city_pop_df.ix[0, 'city_id'])
	Out[12]: str

	In [13]: city_names_df.ix[0, 'city_id'] == city_pop_df.ix[0, 'city_id']
	Out[13]: False

## Solutions. 
Which option is best will depend on the specifics of how your data is dirty.

### Option 1. Apply a parsing function to parse the data:

	:::python
	def parse(x):
    try:
        return int(x)
    except ValueError:
        return np.nan

	In [20]: city_pop_df['city_id'] = city_pop_df['city_id'].apply(parse)

	In [21]: city_pop_df.dtypes
	Out[21]:
	city_id            float64
	city_population      int64
	dtype: object

	In [22]: city_names_df.merge(city_pop_df)
	Out[22]:
	   city_id   city_name  city_population
	0        1      Dublin            52105
	1        2  Pleasanton            74110
	2        3    Millbrae            22424
	3        4    Richmond           107571

### Option 2. Search for non-number string and replace when with NaN:

	:::python
	In [24]: import re

	In [25]: city_pop_df['city_id'] = city_pop_df['city_id'].replace(re.compile('\D*'), np.nan).astype(np.float)

	In [26]: city_names_df.merge(city_pop_df)
	Out[26]:
	   city_id   city_name  city_population
	0        1      Dublin            52105
	1        2  Pleasanton            74110
	2        3    Millbrae            22424
	3        4    Richmond           107571

### Option 3. Make a new file with only the good rows:

	:::console
	$ # keep the column headers
	$ head -n1 city-populations.csv > cleaned-city-populations.csv
	$ grep -E '^[0-9]+,' city-populations.csv >> cleaned-city-populations.csv
 
Load new the file (the cleaning also removed the column headers):
 
    :::python
	In [33]: clean_pop_df = pd.read_csv('cleaned-city-populations.csv')
	
	In [34]: city_names_df.merge(clean_pop_df)
	Out[34]:
	   city_id   city_name  city_population
	0        1      Dublin            52105
	1        2  Pleasanton            74110
	2        3    Millbrae            22424
	3        4    Richmond           107571

### Option 4. Make a new file using csvkit

[`csvkit`](https://csvkit.readthedocs.org/) provides a familiar command line interface designed to work with csv files. The grep command in option 3 above would be difficult to change to apply to the 31st column in a 50 column wide csv file, but `csvgrep` allows columns to be identified by name or number.

	:::console
	$ csvgrep -r '[0-9]+' -c city_id city-populations.csv > cleaned-city-populations2.csv
	
Load the new file:
	
    :::python
	In [33]: clean_pop_df = pd.read_csv('cleaned-city-populations2.csv')
	
	In [34]: city_names_df.merge(clean_pop_df)
	Out[34]:
	   city_id   city_name  city_population
	0        1      Dublin            52105
	1        2  Pleasanton            74110
	2        3    Millbrae            22424
	3        4    Richmond           107571

If you do use shell commands to alter the files, make sure you either keep the commands in a shell script file or call them directly from your python script so that your work can be exactly reproduced given the raw data. Shell commands can be called from IPython either by prefacing the line with `!` or with the `%%bash` cell magic function.