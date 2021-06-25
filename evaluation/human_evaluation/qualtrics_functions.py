# %%
# Import packages

import numpy as np
import pandas as pd
from pathlib import Path
import os
import sys
from zipfile import ZipFile

from sklearn.metrics import accuracy_score, f1_score, \
    precision_score, recall_score, classification_report, \
    confusion_matrix, cohen_kappa_score

from statistics import mean, median, StatisticsError
import math

# %%
# Function for getting ratings dataframes

def get_ratings_df(survey_name, sentence_pairs_csv, groupnum, introblock=0, drop_na = True):
    for root, _, files in os.walk('source'):
        for f in sorted(files, reverse=True):
            file_path = os.path.join(root, f)
            p = Path(file_path)
            file_suffix = p.suffix.lower()
            file_stem = p.stem.replace("+","").lower()
            if file_suffix == '.zip' and file_stem.startswith(survey_name):
                with ZipFile(file_path,'r') as zf:
                    ratings_df = pd.read_csv(zf.open(zf.namelist()[0]), header = 0)
                break

    sentence_pairs_df = pd.read_csv(sentence_pairs_csv, index_col = 0)
    sentence_pairs_df['group'] = groupnum
    

    # Select relevant subset of columns, drop NA values, reindex columns
    ratings_df = ratings_df.iloc[2:,17+introblock:]
    if drop_na == True:
        ratings_df = ratings_df.dropna()
    ratings_df.columns = sentence_pairs_df['qid']

    # Import ratings_df for internal evaluation
    
    for i in range(sentence_pairs_df.shape[0]):
        row = sentence_pairs_df.iloc[i,:]
        og = row['og']
        if og == 2:
            sentence_pairs_df.loc[i,['sent1','sent2']] = sentence_pairs_df.loc[i,['sent2','sent1']].values
            sentence_pairs_df.loc[i,'og'] = 1

            for j in range(ratings_df.shape[0]):
                flippedrating = ratings_df.iloc[j,i]
                ratings_df.iloc[j,i] = '2' if flippedrating == '1' else '1'

    y_model = [2 for i in range(ratings_df.shape[1])] # sentence_pairs_df['og'].tolist()

    return sentence_pairs_df, ratings_df, y_model

# %%
# Function for creating interrater dataframe

def get_inter_ratings_df(sentence_pairs_df, ratings_df):
    
    qid_subset = set()
    qnum_subset = []

    # Keep only first question if repeated
    for i in range(sentence_pairs_df.shape[0]):
        row = sentence_pairs_df.iloc[i,:]
        qid = row['qid']
        if qid not in qid_subset:
            qid_subset.add(qid)
            qnum_subset.append(i)
    
    inter_sentences_df = sentence_pairs_df.iloc[qnum_subset,:]
    
    inter_ratings_df = ratings_df.iloc[:,qnum_subset]
    
    return inter_sentences_df, inter_ratings_df

# %%
# Function for creating intrarater dataframe

def calculate_intrarater_kappas(sentence_pairs_df, ratings_df):
    
    qid_subset = set()
    repeated_subset = []

    # Keep only repeated questions
    for i in range(sentence_pairs_df.shape[0]):
        row = sentence_pairs_df.iloc[i,:]
        qid = row['qid']
        if qid in qid_subset:
            repeated_subset.append(qid)
        qid_subset.add(qid)
    
    intra_sentences_df = sentence_pairs_df[sentence_pairs_df['qid'].isin(repeated_subset)]
    
    intra_ratings_df = ratings_df[repeated_subset]
    intra_rat1_df = intra_ratings_df.iloc[:,[i for i in range(intra_ratings_df.shape[1]) if i % 2 == 0]]
    intra_rat2_df = intra_ratings_df.iloc[:,[i for i in range(intra_ratings_df.shape[1]) if i % 2 == 1]]
    
    intrarater_kappas = dict()

    for i in range(intra_rat1_df.shape[0]):
        rater = intra_rat1_df.iloc[i,:].name
        intrarater_kappa = cohen_kappa_score(intra_rat1_df.iloc[i,:], intra_rat2_df.iloc[i,:])
        intrarater_kappas[rater] = intrarater_kappa
    
    return intrarater_kappas

# %%
# Function for kicking out judges with low intrarater kappa

def kick_out_intra_judges(sentence_pairs_df, ratings_df, kappa_threshold):

    og_num_judges = ratings_df.shape[0]

    intra_kappas = calculate_intrarater_kappas(sentence_pairs_df, ratings_df)
    
    to_kick = set()
    
    for key, value in intra_kappas.items():
        if value < kappa_threshold:
            to_kick.add(key)

    filt_ratings_df = ratings_df.drop(to_kick)

    num_judges = filt_ratings_df.shape[0]

    print(f"{num_judges}/{og_num_judges} judges left, kappa threshold: {kappa_threshold}")

    return filt_ratings_df

# %%
# Function for calculating pairwise kappas and mean

def calculate_kappas(ratings_df):
    seen_judge_duo = []
    kappa_pairs = []
    kappas = []
    
    # #Calculate kappas between judges
    for i in range(ratings_df.shape[0]):
        for j in range(ratings_df.shape[0]):
            if i != j:
                judge1_index = ratings_df.index[i]
                judge2_index = ratings_df.index[j]
                if {judge1_index, judge2_index} not in seen_judge_duo:
                    seen_judge_duo.append({judge1_index, judge2_index})
                    
                    y_judge1 = ratings_df.iloc[i,:].tolist()
                    y_judge2 = ratings_df.iloc[j,:].tolist()
                    kappa_pair = cohen_kappa_score(y_judge1, y_judge2)
                    kappa_pairs.append([judge1_index,judge2_index,kappa_pair])
                    kappas.append(kappa_pair)
                    # print(f"Cohen's kappa between judge {judge1_index} and {judge2_index}: {kappa_pair}")

    return kappa_pairs, mean(kappas)

# %%
# Function for calculating kappas for the models

def get_kappa_groups(sentence_pairs_df, ratings_df):
    
    kappa_groups = []
    
    for model in sentence_pairs_df['model'].unique():
        subset = sentence_pairs_df[sentence_pairs_df['model'] == model]['qid'].values
        kappa_pairs, mean_kappa = calculate_kappas(ratings_df[subset])
        kappa_groups.append(['model',model,kappa_pairs,mean_kappa])

    for source in sentence_pairs_df['source'].unique():
        subset = sentence_pairs_df[sentence_pairs_df['source'] == source]['qid'].values
        kappa_pairs, mean_kappa = calculate_kappas(ratings_df[subset])
        kappa_groups.append(['source',source,kappa_pairs,mean_kappa])
    
    return kappa_groups

# %%
# Function for kicking out judges with low kappa scores

def kick_out_judges(ratings_df, kick_out_rate):

    for i in range(math.ceil(kick_out_rate*ratings_df.shape[0])):
        
        kappa_pairs, mean_kappa = calculate_kappas(ratings_df)
        
        if i == 0:
            og_mean_kappa = mean_kappa
            og_num_judges = ratings_df.shape[0]

        kappas = dict()

        for i in kappa_pairs:
            for j in i[0:2]:
                if j in kappas:
                    kappas[j].append(i[2])
                else:
                    kappas[j] = [i[2]]

        median_kappas = dict()

        for key, value in kappas.items():
            value = median(value)
            median_kappas[key] = value

        # print(median_kappas)

        weakest_link = min(median_kappas, key=median_kappas.get)

        ratings_df = ratings_df.drop(weakest_link)

    num_judges = ratings_df.shape[0]

    if num_judges > 1:
        kappa_pairs, mean_kappa = calculate_kappas(ratings_df)
        print(f"{num_judges}/{og_num_judges} judges left, mean_kappa: {og_mean_kappa} -> {mean_kappa}")
    else:
        print('Not enough judges left to calculate mean kappa')

    return ratings_df

# %%
# Function for creating dataset of questions where all judges agreed

def everyone_agreed(sentence_pairs_df, ratings_df, majority=False):
    
    agreement = []

    for i in range(ratings_df.shape[1]):
        row = ratings_df.T.iloc[i,:]
        ratings = row.values
        qid = row.name
        if majority == False:
            if all(j == ratings[0] for j in ratings):
                agreement.append(qid)
        else:
            if sum(j == ratings[0] for j in ratings) > math.ceil(ratings_df.shape[0]/2):
                agreement.append(qid)

    agreement_df = pd.DataFrame(ratings_df[agreement].astype(int).agg(lambda x: pd.Series.mode(x)[0]).astype(int).astype(str), columns = ['y_judges'])

    agreement_df = sentence_pairs_df.merge(agreement_df, left_on = 'qid', right_on = 'qid')

    agreement_df['y_model'] = '2'

    return agreement_df

# %%
# Function for calculating F1 groups

def get_f1_groups(agreement_df):
    
    f1_groups = []

    f1_groups.append(f1_score(agreement_df['y_judges'], agreement_df['y_model'], average='macro'))

    for model in agreement_df['model'].unique():
        subset = agreement_df[agreement_df['model'] == model]
        y_judges = subset['y_judges']
        y_model = subset['y_model']
        f1 = f1_score(y_judges, y_model, average='macro')
        f1_groups.append(['model',model,f1])

    for source in agreement_df['source'].unique():
        subset = agreement_df[agreement_df['source'] == source]
        y_judges = subset['y_judges']
        y_model = subset['y_model']
        f1 = f1_score(y_judges, y_model, average='macro')
        f1_groups.append(['source',source,f1])

    return f1_groups

# %%
# Create annotation_matrix

def get_annotation_matrix(ratings_df):
    
    annotation_matrix = []
    
    for i in range(ratings_df.shape[0]):
        row = ratings_df.iloc[i,:]
        rater = row.name
        for i, irat in enumerate(row):
            question = row.index[i]
            rating = irat
            annotation_matrix.append([rater, question, rating])
    
    return annotation_matrix
