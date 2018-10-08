Names: Evan Amason and Mary Clare Shen

1. In general, Laplace smoothing adds some constant count to to all possible events. For this file, Laplace smoothing adds a count of .1 to every possible pair of expected and observed characters from the alphabet. If we didn't use Laplace smoothing, when we call the prob function we'd be calling log on values of 0, which is undefined.

2. EditDistance.py takes in the name of a file to store the model in and the name of a file to generate the modle from. We would run this command:

EditDistance.py --store ed.pkl --source /data/spelling/wikipedia_misspellings

3. LanguageModel.py supports unigrams and bigrams.

4. LanguageModel.py uses Laplace smoothing where the value added to the count is alpha.

5. __contains__() defines the class's implementation for the "in" method. In LanguageModel.py specifically, __contains__() checks if the letter w is in the model's vocabulary.

6. get_chunks() uses the "yield" keyword to return a generator that will not actually get a chunk until the generator is iterated over and will then forget the chunk when it iterates to the next one.

7. LanguageModel.py takes in the name of the file to store the model in, optionally takes in an alpha and/or vocab size, and takes in the name of the file to generate the model from. If there isn't an input value for alpha or vocab, the default values are 0.1 and 40000 respectivelly. To generate the specific example we want, we would run this command:

LanguageModel.py -s lm.pkl /data/gutenberg/*.txt

