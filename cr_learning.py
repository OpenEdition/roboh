#!/usr/bin/env python

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
    vectorizer = CountVectorizer(input='filename', ngram_range=(1,2), analyzer='word', max_df=0.5, max_features = 5000)
    x_train = vectorizer.fit_transform(list_f)
    transformer = TfidfTransformer(norm='l2', use_idf=False)
    tfidf_train = transformer.fit_transform(x_train)
    X_tag = addTagVector(tfidf_train, 'data/train/tag')
    X = addSentVector(X_tag, '/tmp')

    #X=tfidf_train
    Y = getYVector('data/train/notag')
    print('\t Training...')
    clf = SGDClassifier(alpha=1e-06, n_iter=50, penalty='l2', loss='hinge')
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


##@brief Train the classifier on texts's file stored in two directory
# and save model in crmodel.pkl
# @param x_idf sparse.csr_matrix :  matrix will be convert in numpy array (not really good for memory...
# @param dir_tag str : directory with same files with enhanced named entity tag
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
    print(x_feat.shape)
    print(x_idf.toarray().shape)
    #Ajout des features EN aux fichiers vectorisés
    X = np.concatenate((x_feat, x_idf.toarray()), axis=1)
    print(X.shape)
    return X


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


##@brief Train the classifier on texts's file stored in two directory
# and save model in crmodel.pkl
# @param X numpy array:  matrix will be convert in numpy array (not really good for memory...
# @param dir_tag str : directory with same files with enhanced sentiment analysis sentence by sentence
# @param opinion list : list of string tag
# @return a new numpy array enhanced by new features
# @todo handle properly path (not relative)
def addSentVector(x_idf, dir_sent, opinion=['positive', 'negative']):
    #Ajout des features entités nommées. On regarde la fréquence de chaque
    list_f_tag = getFiles(dir_sent)
    list_feat= []
    for f in list_f_tag:
        with open (f, "r") as f_tag:
            lst_tag = json.dumps(f_tag.readlines()[1])
            print(type(lst_tag))
        size = len(lst_tag)
        step = int(size / 10)
        for i in range(0, 10):
            part_lst = [i*step:size]
            
        words_nbr = len(txt_tag.split())
        row = []
        for entity in tag:
            row.extend(addNedFeatures(entity, txt_tag, char_nbr, words_nbr))
        list_feat.append(row)
    x_feat = np.array(list_feat)
    print(x_feat.shape)
    print(x_idf.toarray().shape)
    #Ajout des features EN aux fichiers vectorisés
    X = np.concatenate((x_feat, x_idf.toarray()), axis=1)
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
        #prédiction à partir de x_test
        predicted = clf.predict(x_test)
        print(predicted, len(predicted))
        y = getYVector('data/test/notag')
        print(precision_recall_fscore_support(y, predicted, average='binary', pos_label=0))
    else:
        raise NameError('This datasource don\'t exit!')


