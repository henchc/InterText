# InterText
Discovers intertextualities.
Algorithm uses fuzzywuzzy string matching and special doublet hashing by Zach Schollz https://github.com/schollz/string_matching in order to lookup fuzzy matches.


InterText takes 4 arguments:

```
python InterText2.py <text a> <text b> <n-gram window> <sim. threshold>
```

# InterText output:
When a comparison is finished, InterText writes an HTML file with hyperlinks to the respective matches. Texts are printed side-by-side for comparison.

# Dependencies
InterText is written in Python 3 with only one dependency: fuzzywuzzy (pip install fuzzywuzzy). fuzzywuzzy is a Python library that simplifies the matching process, drawing primarily from the levenshtein distance. The n-gram function is excerpted from NLTK, but included in the InterText code.
