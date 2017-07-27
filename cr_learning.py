#!/usr/bin/env python3

__author__ ='morban'
__email__ = 'mathieu.orban@openedition.org'

import sys
action = sys.argv[1]

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

    
##@brief Get files from a directory, files are splitten in 
# and two directores corresponding to their classification
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
    vectorizer = CountVectorizer(input='filename', ngram_range=(1,2), analyzer='word', stop_words = 'english', max_df=0.3, max_features = 5000)
    x_train = vectorizer.fit_transform(list_f)
    transformer = TfidfTransformer(norm='l1', use_idf=False)
    tfidf_train = transformer.fit_transform(x_train)
    #X = addTagVector(tfidf_train, 'data/train/tag')
    X_tag = addTagVector(tfidf_train, 'data/train/tag')
    X = addSentVector(X_tag, '/tmp/train/tag')

    #X=tfidf_train
    Y = getYVector('data/train/notag')
    print('\t Training...')
    clf = SGDClassifier(alpha=1e-06, n_iter=50, penalty='l2', loss='log')
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
    print(x_idf.shape)
    return x_idf


##@brief Append to matrix bag of words the tag column features
# @param x_idf sparse.csr_matrix :  matrix will be convert in numpy array (not really good for memory...
# @param dir_tag str : directory (file and subdirectory must match with train witness file)
# @param tag list : list of string tag
# @return a new numpy array enhanced by new features
# @todo handle properly path (not relative)
def addTagVector(x_idf, dir_tag, tag=['<pers>', '<time>', '<loc>']):
    #Ajout des features entités nommées. On regarde la fréquence de chaque
    list_f_tag = getFiles(dir_tag)
    list_feat= []
    for f in list_f_tag:
        with open (f, "r", encoding='latin-1') as f_tag:
            txt_tag = f_tag.read()
        char_nbr = len(txt_tag)
        words_nbr = len(txt_tag.split())
        row = []
        for entity in tag:
            row.extend(addNedFeatures(entity, txt_tag, char_nbr, words_nbr))
        list_feat.append(row)
    x_feat = np.array(list_feat)
    #Ajout des features EN aux fichiers vectorisés
    X = np.concatenate((x_feat, x_idf.toarray()), axis=1)
    print(X.shape)
    return X


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
            lst_tag = json.loads(f_tag.readlines()[1])
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
    print(X.shape)
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
    if action == 'train':
        setLearning('data/train/notag')
    elif action == 'test':
        clf = joblib.load('crmodel.pkl')
        list_f_test = getFiles('data/test/notag')
        x_test_idf = loadIdfFeatures(list_f_test)
        x_test = addTagVector(x_test_idf, dir_tag='data/test/tag')
        X = addSentVector(x_test, '/tmp/test/tag')
        #prédiction à partir de x_test
        predicted = clf.predict(X)
        y = getYVector('data/test/notag')
        #print(predicted, y)
        print(precision_recall_fscore_support(y, predicted, average=None, labels=[0,1]))
    else:
        raise NameError('This datasource don\'t exit!')


