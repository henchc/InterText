# InterText
Discovers intertextualities.
Algorithm uses fuzzywuzzy string matching and doublet hashing by Zach Schollz https://github.com/schollz/string_matching .


InterText takes 4 arguments:

```
python InterText2.py <text a> <text b> <n-gram window> <sim. threshold>
```

## output
When a comparison is finished, InterText writes an HTML file with hyperlinks to the respective matches. Texts are printed side-by-side for comparison.

## dependencies
- fuzzywuzzy
- pyprind
