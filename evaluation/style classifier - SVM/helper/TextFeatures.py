import pandas as pd
import string
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from tqdm.auto import tqdm

"""
Decided to go without object-oriented programming to avoid data overhead.
"""

DEBUG_MODE = True

def extract_lexical_features_character_based(sentences):
    cols = []
    s = "sentence"
    df = pd.DataFrame(sentences, columns=[s])

    cols.append("total_chars")
    df[cols[-1]] = df[s].apply(lambda sent: len(sent))

    cols.append("freq_chars_alpha")
    df[cols[-1]] = df.apply(lambda row: len([c for c in row[s] if c.isalpha()]) / row['total_chars'], axis=1)

    cols.append("freq_chars_upper")
    df[cols[-1]] = df.apply(lambda row: len([c for c in row[s] if c.isupper()]) / row.total_chars, axis=1)

    cols.append("freq_chars_digit")
    df[cols[-1]] = df.apply(lambda row: len([c for c in row[s] if c.isdigit()]) / row.total_chars, axis=1)

    cols.append("freq_chars_space") # counts space " " and tabulator "	"
    df[cols[-1]] = df.apply(lambda row: len([c for c in row[s] if c.isspace()]) / row.total_chars, axis=1)

    # frequency by alphabetic letter
    # todo - not sure yet if relevant
    # letters = list("abcdefghijklmnopqrstuvwxyz")
    # for letter in letters:
    #     cols.append(letter)
    #     df[cols[-1]] = df.apply(lambda row: len([c for c in row[s] if c == letter]) / row.total_chars, axis=1)

    # frequency of special characters
    cols.append("freq_chars_special")
    df[cols[-1]] = df.apply(lambda row: len([c for c in row[s] if c in string.punctuation]) / row.total_chars, axis=1)

    return (cols, df)


def extract_lexical_features_word_based(sentences):
    cols = []
    col_data_total_words = []
    col_data_freq_words_short = []
    col_data_avg_word_length = []
    col_data_freq_different_words = []
    s = "sentence"
    df = pd.DataFrame(sentences, columns=[s])

    for sent in tqdm(df[s], total=df.shape[0]):

        tokens = nltk.tokenize.word_tokenize(sent)
        words = [token for token in tokens if not token in string.punctuation]
        
        # total words
        col_data_total_words.append(len(words))
        
        # freq short words
        col_data_freq_words_short.append( len([word for word in words if len(word) < 4]) / col_data_total_words[-1] )

        # average word length
        col_data_avg_word_length.append( sum([len(word) for word in words]) / col_data_total_words[-1] )

        # lexical diversity
        col_data_freq_different_words.append( len(set(words)) / col_data_total_words[-1] )


    cols.append("total_words")
    df[cols[-1]] = col_data_total_words

    cols.append("freq_words_short")
    df[cols[-1]] = col_data_freq_words_short

    cols.append("avg_word_length")
    df[cols[-1]] = col_data_avg_word_length

    cols.append("freq_unique_words")
    df[cols[-1]] = col_data_freq_different_words

    return (cols, df)


def _hapax_legomena_ratio(text):  # # per document only a float value
    # Thank you to Yunita Sari
    # source: https://github.com/yunitata/coling2018/blob/5aa7b24e3ff29235c05e48bcaad3a2bf8a73c5cf/feature_extractor.py#L120-L133
    word_list = text.split(" ")
    fdist = nltk.FreqDist(word for word in word_list)
    fdist_hapax = nltk.FreqDist.hapaxes(fdist)
    return float(len(fdist_hapax)/len(word_list))


def _dislegomena_ratio(text):  # per document only a float value
    # Thank you to Yunita Sari
    # source: https://github.com/yunitata/coling2018/blob/5aa7b24e3ff29235c05e48bcaad3a2bf8a73c5cf/feature_extractor.py#L120-L133
    word_list = text.split(" ")
    vocabulary_size = len(set(word_list))
    freqs = Counter(nltk.probability.FreqDist(word_list).values())
    VN = lambda i:freqs[i]
    return float(VN(2)*1./vocabulary_size)


def extract_vocabulary_richness(sentences):
    cols = []
    s = "sentence"
    df = pd.DataFrame(sentences, columns=[s])

    cols.append("vocab_richness_hapax_legomena")
    df[cols[-1]] = df[s].apply(lambda sent: _hapax_legomena_ratio(sent))

    cols.append("vocab_richness_hapax_dislegomena")
    df[cols[-1]] = df[s].apply(lambda sent: _dislegomena_ratio(sent))

    return (cols, df)


def extract_pos_tags(sentences, universal=False):

    def update_row_with_dict(df,d,idx):
        df.loc[idx,d.keys()] = d.values()

    # todo pos tags -> need a fix number of columns as result to allow for flawless classification later
    nltk_pos_tags = ["$", "''", "(", ")", ",", "--", ".", ":", "CC", "CD", "DT", "EX", "FW", "IN", "JJ", "JJR", "JJS", "LS", "MD", "NN", "NNP", "NNPS", "NNS", "PDT", "POS", "PRP", "PRP$", "RB", "RBR", "RBS", "RP", "SYM", "TO", "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB", "``", "#"]
    universal_tags = ["ADJ", "ADP", "ADV", "CONJ", "DET", "NOUN", "NUM", "PRT", "PRON", "VERB", ".", "X"]

    if universal:
        tags = universal_tags
    else:
        tags = nltk_pos_tags

    num_by_POS_tag = []
    
    s = "sentence"
    df = pd.DataFrame(sentences, columns=[s])

    for sent in tqdm(df[s], total=df.shape[0]):

        tokens = nltk.tokenize.word_tokenize(sent)
        tagged = nltk.pos_tag(tokens)
        if universal:
            tagged = [(word, nltk.tag.map_tag('en-ptb', 'universal', tag)) for word, tag in tagged]
        counts = dict()
        for (i,j) in tagged:
            counts[j] = counts.get(j, 0) + 1
        num_by_POS_tag.append(counts)
    
    df[tags] = 0

    for idx in tqdm(df.index, total=df.shape[0]):
        update_row_with_dict(df,num_by_POS_tag[idx],idx)

    # Verify, whether a different amount of POS tags appear, than predefined.
    if universal:
        if df.shape[1] != 13:
            print(list(df.columns))
            raise Exception(f"For universal tagset, 12 pos tags should exist, but here are {df.shape[1] - 1}")
    else:
        if df.shape[1] != 47:
            print(list(df.columns))
            raise Exception(f"For nltk tagset, 45 pos tags should exist, but here are {df.shape[1] - 1}")
    
    return (tags, df)


def extract_char_trigrams(sentences, vec=None):
    s = "sentence"
    df = pd.DataFrame(sentences, columns=[s])

    # training the vectorizer
    if not vec:
        print("create new vectorizer")
        vec = TfidfVectorizer(analyzer="char", ngram_range=(3, 3), max_df=0.95, min_df=1, max_features=250)
        vec.fit_transform(df[s])

    # apply it to the sentences one by one
    cols = list(map(lambda x: f"/{x}/", vec.get_feature_names()))
    tfidf_scores = []
    df[cols] = 0

    for sent in tqdm(df[s], total=df.shape[0]):
        tfidf_scores.append(vec.transform([sent]).toarray()[0])
    df[cols] = tfidf_scores

    return (cols, df, vec)


def add_all_text_features(df, col_sentences):
    print("lexical features character based")
    (cols, df_sub) = extract_lexical_features_character_based(df[col_sentences])
    df[cols] = df_sub[cols]

    print("lexical features word based")
    (cols, df_sub) = extract_lexical_features_word_based(df[col_sentences])
    df[cols] = df_sub[cols]

    print("lexical features vocabulary richness")
    (cols, df_sub) = extract_vocabulary_richness(df[col_sentences])
    df[cols] = df_sub[cols]

    print("pos tags")
    (cols, df_sub) = extract_pos_tags(df[col_sentences], universal=False)
    df[cols] = df_sub[cols]


    return df