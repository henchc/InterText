# InterText
Discovers intertextualities


InterText takes 5 arguments:

```
python InterText2mp.py <text a> <folder of text bs> <n-gram window> <sim. threshold> <match sens.>
```

1.	Text A – the text to be compared to all others
2.	Folder with Text B(s) – Folder containing all other texts to compare to Text A
3.	N-gram window – Number of words in each unit to compare
4.	Similarity threshold (0-100) – How similar must a word be to be the same word? Uninflected languages such as English will have higher thresholds, highly inflected languages such as Latin will have lower thresholds.
5.	Match Sensitivity (0-1) – How strongly should frequent words be penalized?

# Description
After cleaning the texts (stripping numbers and punctuation), InterText determines word frequencies for Text A and Text B. These word frequencies determine the respective penalty for match sensitivity. InterText then creates n-grams for Text A and Text B and rejoins them as strings of three words. Via multiprocessing (taking advantage of all cores of the CPU), InterText then iterates through every combination of three successive words for each text, first giving a frequency score to the set, and if below the match sensitivity threshold, continues to evaluate the string similarity. Important for languages with generous word order rules, InterText first orders the set of three words for Text A and Text B alphabetically, then compares the string of three words as one for Text A and Text B. If the similarity score is above the threshold, the match is appended to the results.

InterText output:
When a comparison is finished, InterText writes an HTML file with hyperlinks to the respective matches. Texts are printed side-by-side for comparison. An additional CSV file of excerpted matches is also created.

# Dependencies
InterText is written in Python 3 with only one dependency: fuzzywuzzy (pip install fuzzywuzzy). fuzzywuzzy is a Python library that simplifies the matching process, drawing primarily from the levenshtein distance. The n-gram function is excerpted from NLTK, but included in the InterText code.
