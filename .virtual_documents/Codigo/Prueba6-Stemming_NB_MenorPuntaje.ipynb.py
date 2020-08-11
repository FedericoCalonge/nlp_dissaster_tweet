import pandas as pd
import numpy as np
import re
import string


from time import time  # To time our operations
from collections import defaultdict  # For word frequency
from collections import  Counter
import spacy  # For preprocessing

import logging  # Setting up the loggings to monitor gensim


from nltk.corpus import stopwords
from nltk.util import ngrams

from nltk.tokenize import word_tokenize
import gensim
import string
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm
from keras.models import Sequential
from keras.layers import Embedding,LSTM,Dense,SpatialDropout1D
from keras.initializers import Constant
from sklearn.model_selection import train_test_split
from keras.optimizers import Adam



from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
import nltk
from nltk.stem.snowball import SnowballStemmer



#Cargamos dataset train en un dataframe
tweets_train = pd.read_csv('Dataset/train.csv')
tweets_test = pd.read_csv('Dataset/test.csv')
tweets_submission = pd.read_csv('Dataset/sample_submission.csv') 



tweets_train.head(10)


#Dropeamos 'Keyword' y 'Location' ya que no los vamos a utilizar
tweets_train.drop(columns = ['keyword','location'])


tweets_train['cleaned_text']=tweets_train['text'].apply(lambda x: re.sub(r'[0-9_]','',x))


tweets_test['cleaned_text']=tweets_test['text'].apply(lambda x: re.sub(r'[0-9_]','',x))


tweets_train.head(10)


tweets_test.head(10)


x = tweets_train.cleaned_text
y = tweets_train.target



x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)


x_train



from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english", ignore_stopwords=True)

class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        return lambda doc: ([stemmer.stem(w) for w in analyzer(doc)])

count_vect = StemmedCountVectorizer(stop_words='english', lowercase = True)
tweets_train_counts = count_vect.fit_transform(x_train)
tweets_test_counts = count_vect.transform(x_test)
tweets_train_counts.shape


#Bag of Words 
#Vectorizamos los textos de cada tweet
#count_vect = CountVectorizer(stop_words = ('english'), lowercase = True)
#tweets_train_counts = count_vect.fit_transform(x_train)
#tweets_test_counts = count_vect.transform(x_test)
#tweets_train_counts.shape
#print(count_vect.get_feature_names())


#TFIDF
tfidf_transformer = TfidfTransformer()
tweets_train_tfidf = tfidf_transformer.fit_transform(tweets_train_counts)
tweets_test_tfidf = tfidf_transformer.transform(tweets_test_counts)


tweets_train_tfidf.shape






tweets_train_NB = MultinomialNB().fit(tweets_train_tfidf, y_train)
predicted = tweets_train_NB.predict(tweets_test_tfidf)
np.mean(predicted == y_test)


#Prueba4 parametros, maxima iteracion = 10, quedaba en loss modified huber
#Prueba5 es el que da abajo
parameters = {'alpha': ([1.0])}

gs_NB = GridSearchCV(tweets_train_NB, parameters, n_jobs=-1)
gs_NB = gs_NB.fit(tweets_train_tfidf, y_train)




gs_NB_best = gs_NB.best_estimator_
gs_NB.best_score_
gs_NB.best_params_


best_NB = gs_NB_best.fit(tweets_train_tfidf, y_train)


predicted = best_NB.predict(tweets_test_tfidf)
np.mean(predicted == y_test)


test_text = tweets_test.cleaned_text
test_text_counts = count_vect.transform(test_text)
test_text_tfidf = tfidf_transformer.transform(test_text_counts)
test_target_predicted = best_NB.predict(test_text_tfidf)


tweets_submission.target = test_target_predicted
tweets_submission.to_csv("submission.csv",index=False)


import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10,7))
g = sns.barplot(x= tweets_submission.target.value_counts().index, y= tweets_submission.target.value_counts().values, orient='v', palette= 'husl', hue= tweets_submission.target.value_counts().index, dodge=False)
g.set_title("Tweets Test", fontsize=22)
g.set_xlabel("Tipo de noticia", fontsize=16)
g.set_ylabel("Cantidad de tweets", fontsize=16)



