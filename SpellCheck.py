import spacy
import argparse
import string
import EditDistance
import LanguageModel

class SpellChecker():

    nlp = spacy.load("en", pipeline=["tagger", "parser"])
    BLANK = '%'
    ALPHA = string.ascii_lowercase + BLANK

    def __init__(self, max_distance, channel_model = None, 
            language_model = None):

        self.channel_model = channel_model
        self.language_model = language_model
        self.max_distance = max_distance

    def load_channel_model(self, fp):
        self.channel_model = EditDistance.EditDistanceFinder()
        self.channel_model.load(fp)

    def load_language_model(self, fp):
        self.language_model = LanguageModel.LanguageModel()
        self.language_model.load(fp)

    def bigram_score(self, prev_word, focus_word, next_word):
        firstPairProb = self.language_model.bigram_prob(prev_word, focus_word)
        secondPairProb = self.language_model.bigram_prob(focus_word, next_word)
        return (firstPairProb + secondPairProb) / 2

    def unigram_score(self, word):
        return self.language_model.unigram_prob(word)

    def cm_score(self, error_word, corrected_word):
        return self.channel_model.prob(error_word, corrected_word)

    def inserts(self, word):
        returnList = []
        for i in range(len(word) + 1):
            for letter in self.ALPHA:
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
            for letter in self.ALPHA:
                testSub = word[:i] + letter + word[i+1:]
                if testSub in self.language_model:
                    returnList.append(testSub)

        return returnList

    def transpositions(self, word):
        returnList = []
        for i in range(len(word) - 1):
            testSwap = word[:i] + word[i + 1] + word[i] + word[i+2:]
            if testSwap in self.language_model:
                returnList.append(testSwap)

        return returnList

    def generate_candidates(self, word):
        if word in string.punctuation:
            return [word]
        elif word == '\n':
            return [word]
        return list(self.generate_candidates_helper(word, self.max_distance))[1:]

    def generate_candidates_helper(self, word, current_dist):
        insList = self.inserts(word)
        delList = self.deletes(word)
        subList = self.substitutions(word)
        swapList = self.transpositions(word)
        candidates = set(insList + delList + subList + swapList)
        if current_dist == 1:
            return candidates
        else:
            total_candidates = set(candidates)
            new_dist = current_dist - 1
            for w in candidates:
                new_candidates = self.generate_candidates_helper(w, new_dist) 
                total_candidates.update(new_candidates)
            return total_candidates
    
    def check_sentence(self, sentence, fallback=False):
        returnList = []
        for i in range(len(sentence)):
            if i != 0:
                prev = sentence[i-1]
            else:
                prev = '<s>'
            word = sentence[i]
            if i + 1 < len(sentence):
                next = sentence[i + 1]
            else:
                next = '</s>'

            if word in self.language_model:
                returnList.append([word])
            else:
                candidates = self.generate_candidates(word)
                if candidates == [] and fallback:
                    returnList.append([word])
                else:
                    score_fn = lambda c: self.suggestion_score(prev, word, c, next)
                    candidates.sort(key = score_fn, reverse=True)
                    returnList.append(candidates)
        return returnList

    def suggestion_score(self, prev_word, obs_word, focus_word, next_word):
        unigram_prob = self.unigram_score(focus_word)
        bigram_prob = self.bigram_score(prev_word, focus_word, next_word)
        lm_score = 0.5 * (unigram_prob + bigram_prob)
        cmscore = self.cm_score(obs_word, focus_word)
        return lm_score + cmscore

    def check_text(self, text, fallback=False):
        doc = self.nlp(text)
        sentences = list(doc.sents)

        all_sentences = []
        for sent in sentences:
            sent_list = [ str(t).lower() for t in sent]
            all_sentences += self.check_sentence(sent_list, fallback) 
        return all_sentences

    def autocorrect_sentence(self, sentence):
        checks = self.check_sentence(sentence, True)

        tokens = []
        for candidates in checks:
            tokens.append(candidates[0])

        return tokens

    def autocorrect_line(self, line):
        doc = self.nlp(line)
        sentences = list(doc.sents) 

        sentence_list = []
        for sent in sentences:
            sent_list = [str(t).lower() for t in sent]
            sentence_tokens = self.autocorrect_sentence(sent_list)
            sentence_list += sentence_tokens
        
        return sentence_list

    def suggest_sentence(self, sentence, max_suggestions):
        checks = self.check_sentence(sentence)
        returnList = []

        for candidates in checks:
            if len(candidates) == 1:
                returnList.append(candidates[0])
            else:
                returnList.append(candidates[0:max_suggestions])
                
        return returnList

    def suggest_text(self, text, max_suggestions):
        doc = self.nlp(text)
        sentences = doc.sents
        returnList = []
        for sent in sentences:
            sent_list = [str(t) for t in sent]
            returnList += self.suggest_sentence(sent_list, max_suggestions)
        return returnList

