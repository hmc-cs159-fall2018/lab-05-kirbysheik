import spacy
import argparse
import string
import EditDistanceFinder
import LanguageModel

class SpellChecker():

    nlp = spacy.load("en", pipeline=["tagger", "parser"])
    alphabet = [string.ascii_lower] + ["%"]
    BLANK = '%'

    def __init__(self, channel_model = None, 
            language_model = None, max_distance)):

        self.channel_model = channel_model
        self.language_model = language_model
        self.max_distance = max_distance

    def load_channel_model(self, fp):
        self.channel_model = EditDistanceFinder()
        self.channel_model.load(fp)

    def load_language_model(self, fp):
        self.language_model = LanguageModel()
        self.language_model.load(fp)

    def bigram_score(self, prev_word, focus_word, next_word):
        firstPairProb = self.language_model.bigram_prob(prev_word, focus_word)
        secondPairProb = self.language_model.bigram_prob(focus_word, next_word)
        return (firstPairProb + secondPairProb) / 2

    def unigram_score(self, word):
        return self.language_model.unigram_prob(word)

    def cm_socre(self, error_word, corrected_word):
        return self.channel_model.prob(error_word, corrected_word)

    def inserts(self, word):
        returnList = []
        for i in range(len(word) + 1):
            for letter in alphabet:
                testIns = word[:i] + letter + word[i:]
                if testIns in self.language_model:
                    returnList.append(testIns)

        return returnList

    def deletes(self, word):
        returnList = []
        for i in range(len(word)):
            testDel = word[:i] + word[i+1:]
            if testDel in self.language_model:
                returnList.append(testDel)

        return returnList

    def substitutions(self, word):
        returnList = []
        for i in range(len(word)):
            for letter in alphabet:
                testSub = word[:i] + letter + word[i+1:]
                if testSub in self.language_model:
                    returnList.append(testSub)

        return returnList

    def generate_candidates(self, word):
        return list(self.generate_candidates_helper(word, self.max_distance))

    def generate_candidates_helper(self, word, current_dist):
        insList = self.inserts(word)
        delList = self.deletes(word)
        subList = self.substitutions(word)
        candidates = set(insList + delList + subList)
        if current_dist == 1:
            return candidates
        else:
            total_candidates = candidates
            new_dist = current_dist - 1
            for w in candidates:
                new_candidates = self.generate_candidates_helper(w, new_dist) 
                total_candidates.update(new_candidates)
            return total_candidates
    
    def check_sentence(self, sentence, fallback=False):
        returnList = []
        for word in sentence:
            if word in self.language_model:
                returnList.append([word])
            else:
                candidates = self.generate_candidates(word)
                if candidates == [] and fallback:
                    returnList.append([word])
                else:
                    candidates.sort(key = lambda x: .5*(cmscore(x,word)+unigram_score(word)), reverse=True)
                    returnList.append(candidates)
        return returnList

    def check_text(self, text, fallback=False):
        doc = nlp(text)

        all_sentences = []
        for sentence in doc:
            all_sentences += self.check_sentence(sentence, fallback) 
        return all_sentences

    def autocorrect_sentence(self, sentence):
        checks = self.check_sentence(sentence, True)

        tokens = []
        for candidates in checks:
            tokens.append(candidates[0])

        return tokens

    def autocorrect_line(self, line):
        tokens = nlp(line)
        sentence_list = []
        for sentence in tokens:
            sentence_tokens = self.autocorrect_sentence(sentence)
            sentence_list += " ".join(sentence_tokens)
        new_line = " ".join(sentence_list)
        return new_line

    def suggest_sentence(self, sentence, max_suggestions):
        checks = self.check_sentence(sentence)
        returnList = []
        for candidates in checks:
            if len(candidates)==1:
                returnList += candidates[0]
            else:
                best = candidates[0]
                best_score = .5*(unigram_score(best) + bigram_score('</s>',best, candidates[1]))
                for i in range(len(1,candidates):
                    prev_word = candidates[i-1]
                    focus_word = candidates[i]
                    next_word = candidates[i+1]
                    new_score = .5*(unigram_score(focus_word) +
                                    bigram_score(prev_word, focus_word, next_word))
                    if new_score > best_score:
                        best = new_word
                        best_score = new_score
                    returnList += best
        return returnList

    def suggest_text(self, text, max_suggestions):
        tokens = nlp(text)
        returnList = []
        for sentence in tokens:
            returnList += suggest_sentence(sentence, max_suggestions)
	return returnList

