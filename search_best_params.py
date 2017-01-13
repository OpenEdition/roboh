from __future__ import print_function
import numpy as np
from pprint import pprint
from time import time
import logging
import glob
import re
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline

list_stop_words = []
with open('stop_list_fr.txt', "r") as f:
    list_stop_words = [ st.rstrip() for st in f.readlines()]

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier()),
])

parameters = {
    'vect__analyzer': ('word',),
    'vect__stop_words': (list_stop_words,'english', None),
    'vect__max_df': (0.1, 0.3, 0.5),
    'vect__max_features': (3000, 5000, 7000),
    'vect__ngram_range': ((1, 1), (1, 2), (1,3)),  # unigrams or bigrams
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    'clf__loss' : ('hinge', 'log'),
    'clf__alpha': (0.00001, 0.000001),
    'clf__penalty': ('l2', 'elasticnet'),
    'clf__n_iter': (10, 50, 80),
   }



if __name__ == "__main__":
    #Get data train 
    categories=['CR', 'NCR']
    print(categories)
    data = load_files('./data/train/notag', categories=categories)
    print("%d documents" % len(data))
    print("%d categories" % len(data.target_names))
    grid_search = GridSearchCV(pipeline, parameters, n_jobs = 12, verbose =1)
    print("Performing grid search...")
    print("pipeline:", [name for name, _ in pipeline.steps])
    print("parameters:")
    pprint(parameters)
    X, Y = data.data, data.target
    t0 = time()
    grid_search.fit(X, Y)
    print("done in %0.3fs" % (time() - t0))
    print()
    print("Best score: %0.3f" % grid_search.best_score_)
    print("Best parameters set:")
    best_parameters = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))



