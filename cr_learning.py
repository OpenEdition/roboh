#!/usr/bin/env python3

__author__ ='morban'
__email__ = 'mathieu.orban@openedition.org'

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import glob
import numpy as np
import re
from sklearn import cross_validation
from sklearn.metrics import precision_recall_fscore_support
from sklearn.externals import joblib
import pickle
from sklearn.linear_model import SGDClassifier
import json

import argparse
parser = argparse.ArgumentParser(description='Training or inference script in order to classifiy review of book from an article on hypotheses.org platform')

parser.add_argument('-s','--dataset', metavar='dataset', type=str, help='Path to datatset')
parser.add_argument('-a','--action', metavar='action', required=True, type=str, help='train or test .... Make your choice')
parser.add_argument('-t','--tag_data', metavar='tag_data', type=str)
parser.add_argument('-o','--output', metavar='output', type=str)


args = parser.parse_args()


##@brief Get files from a directory, files are splitten in 
# and two directories corresponding to their classification
# @param dir_name  st : relative path to directory
# @todo handle properly path (not relative)
# @return A list of path to files order by classification
def getFiles(dir_name):
    list_f = glob.glob('{}/CR/*'.format(dir_name))
    list_f_NCR = glob.glob('{}/NCR/*'.format(dir_name))
    list_f.extend(list_f_NCR)
    return list_f

##@brief Train the classifier on texts's file stored in two directory
# and save model in crmodel.pkl
# @param dir_name  st : relative path to directory. Default: 'data/train/notag'
# @todo handle properly path (not relative)
def setLearning(dir_name='data/train/notag') :
    list_f = getFiles(dir_name)
    #Vectorize a bag of words and add term frequency (tfidf without idf) 
    vectorizer = CountVectorizer(input='filename', ngram_range=(1,1), analyzer='word', stop_words = 'english', max_df=0.5, max_features = 3000)
    x_train = vectorizer.fit_transform(list_f)
    transformer = TfidfTransformer(norm='l2', use_idf=True)
    tfidf_train = transformer.fit_transform(x_train)
    tag_path = args.tag_data
    #X = addTagVector(tfidf_train, 'data/train/tag')
    X_tag = addTagVector(tfidf_train, tag_path)
    X = addSentVector(X_tag, tag_path)

    #X=tfidf_train
    Y = getYVector(dir_name)
    print('\t Training...')
    clf = SGDClassifier(alpha=1e-05, n_iter=50, penalty='elasticnet', loss='log')
    clf.fit(X, Y)

    print('\t Scoring 5-fold cross-validation :')
    scores = ['recall', 'precision', 'f1'] 
    for score in scores:
        result = cross_validation.cross_val_score(clf, X, Y, cv = 5, scoring='%s_micro'%score)
        print('%s_micro'%score, ' : ', result)
    print('\t Saving model')
    joblib.dump(clf, 'crmodel.pkl')
    joblib.dump(vectorizer.vocabulary_, 'vocab.pkl')



##@brief Load the bag of words matrix with tf (features) from a list of files
# @param list_f : list of files (sample) to vectorize
# @return a sparse.csr_matrix
def loadIdfFeatures(list_f):
    #Instancie sac de mots!!
    vectorizer = CountVectorizer(input='filename', ngram_range=(1,2), vocabulary=joblib.load('vocab.pkl'), analyzer='word', max_df=0.5, max_features = 5000)
    vec_words = vectorizer.fit_transform(list_f)
    transformer = TfidfTransformer(norm='l2', use_idf=False)
    x_idf = transformer.fit_transform(vec_words)
    return x_idf


##@brief Append to matrix bag of words the tag column features
# @param x_idf sparse.csr_matrix :  matrix will be convert in numpy array (not really good for memory...
# @param dir_tag str : directory (file and subdirectory must match with train witness file)
# @param tag list : list of string tag
# @return a new numpy array enhanced by new features
# @todo handle properly path (not relative)
def addTagVector(x_idf, dir_tag, tag=['<PERSON>', '<PERIOD>', '<LOCATION>']):
    #Ajout des features entités nommées. On regarde la fréquence de chaque
    list_f_tag = getFiles(dir_tag)
    list_feat= []
    for f in list_f_tag:
        with open (f, "r") as f_tag:
            txt_tag = picklines(f_tag, [1])
        char_nbr = len(txt_tag)
        words_nbr = len(txt_tag.split())
        row = []
        for entity in tag:
            row.extend(addNedFeatures(entity, txt_tag, char_nbr, words_nbr))
        list_feat.append(row)
    x_feat = np.array(list_feat)
    #Ajout des features EN aux fichiers vectorisés
    X = np.concatenate((x_feat, x_idf.toarray()), axis=1)
    return X

def picklines(file_object, lines_num):
    pick_list = [x for i, x in enumerate(file_object) if i in lines_num]
    return pick_list[0] if len(lines_num)==1 else picklist

##@brief Split text in 10 part and attribute a weight between (0, 1) for each part
# @param entity_tag str : tag of name entity
# @param txt_tag str : text to analyse
# @param char_nbr int : number of charcter in the text
# @param words_nbr int : number of word in the text
# @return list (len(list)= =10, value = weight features)
# @todo handle properly path (not relative)
def addNedFeatures(entity_tag, txt_tag, char_nbr, words_nbr):
    index_pos = [match.start() for match in re.finditer(entity_tag, txt_tag)]
    list_feat = []
    for i in range (1, 11):
        nbr_element = 0
        part = int((i * char_nbr) / 10)
        nbr_element = sum (1 for i in index_pos if i <= part)
        if words_nbr != 0:
            freq_el = round (nbr_element / words_nbr , 2)
        else :
            freq_el = 0.0
        list_feat.append(freq_el)
    return list_feat


##@brief Split text in 10 part and attribute a weight between (0, 1) for each part
# @param X numpy array:  matrix will be convert in numpy array (not really good for memory...
# @param dir_sent str : directory with same files with enhanced sentiment analysis sentence by sentence
# @param opinion list : list of string tag
# @return numpy array (enhanced by new features)
def addSentVector(X_in, dir_sent, opinion=['positive', 'negative']):
    #Ajout des features entités nommées. On regarde la fréquence de chaque
    list_f_tag = getFiles(dir_sent)
    row_feat= []
    for f in list_f_tag:
        with open (f, "r") as f_tag:
            lst_tag = json.loads(picklines(f_tag, [2]))
            list_feat= []
            for i in range (1, 11):
                nbr_element = 0
                step = int(len(lst_tag) / 10)
                nbr_element = sum (1 for value in lst_tag[i*step:(i+1)*step] if value in opinion)
                if lst_tag:
                    freq_el = round (nbr_element / len(lst_tag) , 2)
                else :
                    freq_el = 0.0
                list_feat.append(freq_el)
            row_feat.append(list_feat)
    x_feat = np.array(row_feat)
    #Ajout des features EN aux fichiers vectorisés
    X = np.concatenate((x_feat, X_in), axis=1)
    return X


##@brief Get the labeled matrix
# @param dir_name  st : relative path to directory.
# @return a numpy array of (nsample,) shape
# @todo handle properly path (not relative)
def getYVector(dir_name):
    list_f = glob.glob('{}/CR/*'.format(dir_name))
    list_f_NCR = glob.glob('{}/NCR/*'.format(dir_name))
    y_train = [1 for i in range(len(list_f))]
    y_NCR = [0 for i in range(len(list_f_NCR))]
    y_train.extend(y_NCR)
    Y =  np.array(y_train)
    return Y


if __name__ == '__main__':
    dataset = args.dataset
    if args.action == 'train':
        setLearning(dataset)
    elif args.action == 'test':
        clf = joblib.load('crmodel.pkl')
        list_f_test = getFiles(dataset)
        x_test_idf = loadIdfFeatures(list_f_test)
        tag_path = args.tag_data
        x_test = addTagVector(x_test_idf, tag_path)
        X = addSentVector(x_test, tag_path)
        #prédiction à partir de x_test
        predicted = clf.predict(X)
        y = getYVector(dataset)
        print('DATASET TEST: \n{}'.format(y))
        print('DATA PREDICTED: \n{}'.format(predicted))
        precision, recall, f_score, support =precision_recall_fscore_support(y, predicted, average=None, labels=[1,0])
        print("CR,  NCR: {}".format(support))
        print("Precision: {}".format(precision))
        print("Recall: {}".format(recall))
        print("F_score: {}".format(f_score))
    else:
        raise NameError('This datasource don\'t exit!')


