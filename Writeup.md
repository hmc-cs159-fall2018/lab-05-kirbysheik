Names: Evan Amason and Mary Clare Shen

1. In general, Laplace smoothing adds some constant count to to all possible events. For this file, Laplace smoothing adds a count of .1 to every possible pair of expected and observed characters from the alphabet. If we didn't use Laplace smoothing, when we call the prob function we'd be calling log on values of 0, which is undefined.

2. EditDistance.py takes in the name of a file to store the model in and the name of a file to generate the modle from. We would run this command:

python EditDistance.py --store ed.pkl --source /data/spelling/wikipedia_misspellings

3. LanguageModel.py supports unigrams and bigrams.

4. LanguageModel.py uses Laplace smoothing where the value added to the count is alpha.

5. __contains__() defines the class's implementation for the "in" method. In LanguageModel.py specifically, __contains__() checks if the letter w is in the model's vocabulary.

6. get_chunks() uses the "yield" keyword to return a generator that will not actually get a chunk until the generator is iterated over and will then forget the chunk when it iterates to the next one.

7. LanguageModel.py takes in the name of the file to store the model in, optionally takes in an alpha and/or vocab size, and takes in the name of the file to generate the model from. If there isn't an input value for alpha or vocab, the default values are 0.1 and 40000 respectivelly. To generate the specific example we want, we would run this command:

python LanguageModel.py -s lm.pkl /data/gutenberg/*.txt

6. The vast majority of the time, ispell worked better than our code.

7. Our SpellChecker is better at handling uncommon names. ispell is overly aggressive, one example being that it corrects "Eatwell" to "Eat well". Our code left "Eatwell" alone, which was the right thing to do. ispell tended to do better at everything else, both because it has a larger dictionary (our's doesn't have the word calculator) and because it has better handling of punctuation.

8. We think it is interesting that ispell can't handle transpositions, as it failed to fixed recongise. This means that either it wasn't thought about when ispell was developed, or it is more difficult than it sounds. It could also be because you would have to swap the 'z' to get the word into American spelling.

9. We added in a transposition function that would take a word, swap each letter with the letter in front of it, and check if the result is in the Language Model. If it is, we add it as a potential candidate in generate_candidates.

10. One specific example that our updated SpellChecker caught that it didn't previously is the aforementioned "recongise". With our new code for transpositions added, it was able to correct this to "recognise", something that ispell didn't do.

11. Due to a shortage of time, we didn't modify the EditDistanceFinder to make sure that fixing a transposition costs less than two substitutions. Doing so would likely improve the results of our SpellChecker with the transpositions added.