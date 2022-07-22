#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import pandas as pd
import numpy as np
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
from ckiptagger import construct_dictionary
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

host = 4
host = 0

if host == 0:
    path = r'/Users/aron/Documents/GitHub/Perfume/2_NLP'
    dict_file = r'/Users/aron/Documents/GitHub/Perfume/1_Crawler/Resource/dict.xlsx'
    data_file = r'/Users/aron/Documents/GitHub/Perfume/1_Crawler/Resource/data.xls'
    
elif host == 4:
    path = r'/home/rserver/Data_Mining/personal_workspace/yz/Lab/CkipTagger/'
    dict_file = r'/home/rserver/Data_Mining/personal_workspace/yz/Lab/CkipTagger/Resource/dict.xlsx'
    data_file = r'/home/rserver/Data_Mining/personal_workspace/yz/Lab/CkipTagger/Resource/data.xls'

    
# Codebase ......
path_codebase = [r'/Users/aron/Documents/GitHub/Arsenal/',
                 r'/Users/aron/Documents/GitHub/Codebase_YZ/',
                 r'/home/aronhack/stock_predict/Function',
                 r'D:\GitHub\Arsenal',
                 r'D:\Data_Mining\Projects\Codebase_YZ',
                 r'/home/jupyter/Arsenal/20220522',
                 path + '/Function']

for i in path_codebase:    
    if i not in sys.path:
        sys.path = [i] + sys.path
    
import codebase_yz as cbyz
    
path_resource = path + '/Resource'
path_export = path + '/Export'


# ## Import Custom Dictionary

# In[2]:


dict_df = pd.read_excel(dict_file)
dict_df = cbyz.df_lower(df=dict_df, cols=[])
dict_li = dict_df['word'].tolist()
custom_dict = dict((el, 1) for el in dict_li)
custom_dict = construct_dictionary(custom_dict)


# In[3]:


# 2. Load model
# To use GPU:
#    1. Install tensorflow-gpu (see Installation)
#    2. Set CUDA_VISIBLE_DEVICES environment variable, e.g. os.environ["CUDA_VISIBLE_DEVICES"] = "0"
#    3. Set disable_cuda=False, e.g. ws = WS("./data", disable_cuda=False)
# To use CPU:
# https://drive.google.com/drive/folders/105IKCb88evUyLKlLondvDBoh7Dy_I1tm

ws = WS(path_resource + "/data")
pos = POS(path_resource + "/data")
ner = NER(path_resource + "/data")


# ## Inner Function

# In[4]:


print('Bug - string要考慮重疊的問題')

def filter_type(df, col, string, value):
    '''
    Keep rows with one type only
    '''
    assert isinstance(string, list), 'Error'
    loc_df = df.copy()
    type_li = [col + '_' + str(i) for i in range(len(string))]
    
    for i in range(len(string)):
        loc_df[type_li[i]] = np.where(loc_df['title'].str.contains(string[i]), 1, 0)

    loc_df = loc_df.melt(id_vars='index', var_name=col, value_vars=type_li)
    loc_df = loc_df[loc_df['value']==1]
    loc_df = cbyz.df_add_size(df=loc_df, group_by=['index'], col_name='count')
    loc_df = loc_df[loc_df['count']==1]
    loc_df = loc_df[['index', col]]
    
    cond = []
    for i in range(len(type_li)):
        cond.append(loc_df[col]==type_li[i])
        
    loc_df[col] = np.select(cond, value)
    result = df.merge(loc_df, how='left', on='index')
    return result


# ### NLP

# In[5]:


class SentenceGetter(object):
    
    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func = lambda s: [(w, p, t) for w, p, t in zip(s['word'].values.tolist(), 
                                                           s['pos'].values.tolist(), 
                                                           s['tag'].values.tolist())]
        self.grouped = self.data.groupby('sentence').apply(agg_func)
        self.sentences = [s for s in self.grouped]
        
    def get_next(self):
        try: 
            s = self.grouped['Sentence: {}'.format(self.n_sent)]
            self.n_sent += 1
            return s 
        except:
            return None
                
        
def word2df(word_li, pos, y_li=[]):
    result = pd.DataFrame()
    pred_round = False
    
    if len(y_li) == 0:
        y_li = [np.nan for i in range(len(word_li))]
        pred_round = True
    
    for i in range(len(y_li)):
        cur_sentence = word_li[i]
        cur_y = y_li[i]

        # cur_y不是na
        cur_tag = []
        for j in cur_sentence:
            
            if pred_round:
                cur_tag.append(np.nan)
            elif y == 'type':
                if j == cur_y:
                    cur_tag.append(1)
                else:
                    cur_tag.append(0)
            else:
                if j in cur_y:
                    cur_tag.append(1)
                else:
                    cur_tag.append(0)

        new_li = list(zip(cur_sentence,  pos[i], cur_tag))
        new_result = pd.DataFrame(new_li, columns=['word', 'pos', 'tag'])
        new_result['sentence'] = i

        result = result.append(new_result)

    return result        


# ### NLP Features

# In[6]:


def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    
    features = {
        'bias': 1.0, 
        'word.lower()': word.lower(), 
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
            '-1:postag': postag1,
            '-1:postag[:2]': postag1[:2],
        })
    else:
        features['BOS'] = True
    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
            '+1:postag': postag1,
            '+1:postag[:2]': postag1[:2],
        })
    else:
        features['EOS'] = True
        
    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]
def sent2labels(sent):
    return [label for token, postag, label in sent]
def sent2tokens(sent):
    return [token for token, postag, label in sent]


# ## 4. Run the WS-POS-NER pipeline

# In[7]:


data_raw = pd.read_excel(data_file)

# Use to merge original data
data_raw['title_orig'] = data_raw['title']

if 'index' not in data_raw.columns:
    data_raw['index'] = data_raw.index

data = data_raw.copy()

# Preprocessing
data = data.dropna(subset=['title'], axis=0)
data = data[~data['title'].str.contains('廣告')]
data = cbyz.df_lower(df=data, cols=['title', 'brand'])

print('Bug here')
data['title'] = data['title'].apply(cbyz.unicode_filter)
# data['title'] = data['title'].apply(cbyz.unicode_filter, args=('(\u0030-\u007A|\u4E00-\u9FFF)'))

# There are bug in the crawler, so clean title by limiting length of string.
data = data[(data['title'].str.len()>=5) & (data['title'].str.len()<100)]

# data = data[~data['name'].isna()]
# data = data[data.index<=300]

data = data.dropna(subset=['title'], axis=0)
data['title'] = data['title'].str.replace('找相似', '')

data = filter_type(data, 
                   string=['淡香水', '香水', '淡香精', '香精', '古龍水'],
                   value=['淡香水', '香水', '淡香精', '香精', '古龍水'],
                   col='type')

data = filter_type(data, 
                   string=['男', '女', '中性'],
                   value=['男性', '女性', '中性'],
                   col='gender')

print('Bug - title裡面還是有括號')


# In[8]:


y = 'name'
# y = 'brand'
# y = 'type'
y_pred_col = y + '_pred'


# In[9]:


train_raw = data[~data[y].isna()]
title_train = train_raw['title'].tolist()

pred_raw = data[data[y].isna()]
title_pred = pred_raw['title'].tolist()

y_train = train_raw[y].tolist()


# In[10]:


word_sentence_train = ws(
    title_train,
    # sentence_segmentation = True, # To consider delimiters
    # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
    # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
    coerce_dictionary = custom_dict, # words in this dictionary are forced
)

pos_sentence_train = pos(word_sentence_train)
entity_sentence_train = ner(word_sentence_train, pos_sentence_train)


# In[11]:


word_sentence_pred = ws(
    title_pred,
    # sentence_segmentation = True, # To consider delimiters
    # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
    # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
    coerce_dictionary = custom_dict, # words in this dictionary are forced
)

pos_sentence_pred = pos(word_sentence_pred)
entity_sentence_pred = ner(word_sentence_pred, pos_sentence_pred)


# In[12]:


df_train = word2df(word_li=word_sentence_train, pos=pos_sentence_train, y_li=y_train)
df_train = df_train[['sentence', 'word', 'pos', 'tag']]
df_train = cbyz.df_conv_col_type(df=df_train, cols='tag', to='str')
df_train


# In[13]:


df_pred = word2df(word_li=word_sentence_pred, pos=pos_sentence_pred)
df_pred = df_pred[['sentence', 'word', 'pos', 'tag']]
df_pred = cbyz.df_conv_col_type(df=df_pred, cols='tag', to='str')
df_pred


# In[14]:


# 6. Show Results
def print_word_pos_sentence(word_sentence, pos_sentence):
    assert len(word_sentence) == len(pos_sentence)
    for word, pos in zip(word_sentence, pos_sentence):
        print(f"{word}({pos})", end="\u3000")
    return


# In[15]:


# for i, sentence in enumerate(sentence_list):
#     print(f"'{sentence}'")
#     print_word_pos_sentence(word_sentence_list[i],  pos_sentence_list[i])
#     for entity in sorted(entity_sentence_list[i]):
#         print(entity)


# ## Feature Extraction

# In[16]:


getter_train = SentenceGetter(df_train)
sentence_train = getter_train.sentences

getter_pred = SentenceGetter(df_pred)
sentence_pred = getter_pred.sentences


# In[17]:


### Split train and test sets
X = [sent2features(s) for s in sentence_train]
new_y = [sent2labels(s) for s in sentence_train]
X_train, X_test, y_train, y_test = train_test_split(X, new_y, test_size=0.2, random_state=0)
# X_pred


# In[18]:


X_pred = [sent2features(s) for s in sentence_pred]
# new_y = [sent2labels(s) for s in sentence_pred]


# In[19]:


sentence_train


# ### Train a CRF model

# In[20]:


import pycrfsuite
trainer = pycrfsuite.Trainer(verbose=False)

for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)


# In[21]:


trainer.set_params({
#     'c1': 1.0,   # coefficient for L1 penalty
#     'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 50,  # stop earlier

    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})

# Trainimg
trainer.train(path_export + '/ckip_tagger_model.crfsuite')


# In[22]:


trainer.params()


# In[23]:


trainer.logparser.last_iteration


# In[24]:


print(len(trainer.logparser.iterations), trainer.logparser.iterations[-1])


# ## Make predictions
# 
# To use the trained model, create pycrfsuite.Tagger, open the model and use "tag" method:

# In[ ]:


tagger = pycrfsuite.Tagger()
tagger.open(path_export + '/ckip_tagger_model.crfsuite')


# ### Test Set

# In[ ]:


y_test_pred = []

for i in range(len(y_test)):
    new_pred = tagger.tag(X_test[i])
    y_test_pred.append(new_pred)


# In[ ]:


y_test_pred = cbyz.li_flatten(y_test_pred)
y_test = cbyz.li_flatten(y_test)


# In[ ]:


print(classification_report(y_pred=y_test_pred, y_true=y_test))
# print(classification_report(y_pred=y_pred, y_true=y_test, labels=new_classes))


# ### Prediction Set

# In[ ]:


y_pred = []
y_pred_sentence = []
for i in range(len(X_pred)):
    new_pred = tagger.tag(X_pred[i])
    y_pred = y_pred + new_pred
    y_pred_sentence = y_pred_sentence + [i] * len(new_pred)


# In[ ]:


pred_result_raw = df_pred.copy()
assert len(pred_result_raw) == len(pred_result_raw), 'Error'

pred_result_raw['tag'] = y_pred 

# Debug
pred_result_raw['tag_sentence'] = y_pred_sentence 

pred_result_raw = pred_result_raw[pred_result_raw['tag']=='1']
pred_result_raw = pred_result_raw[['sentence', 'word']]
# pred_result_raw


# In[ ]:


# df_pred[~df_pred['tag'].isna()]
if y == 'name':
    pred_result = pred_result_raw                     .pivot_table(index=['sentence'],
                                 values='word',
                                 aggfunc=lambda x: ''.join(x)) \
                    .reset_index()


# In[ ]:


pred_debug = pred_result_raw                 .pivot_table(index=['sentence'],
                             values='word',
                             aggfunc=lambda x: list(x)) \
                .reset_index()

pred_debug = pred_debug.rename(columns={'word':'word_li'})
pred_result = pred_result.merge(pred_debug, how='left', on='sentence')
pred_result


# In[ ]:


pred_raw


# In[ ]:


update_file = pred_raw[['title_orig']].reset_index(drop=True)
update_file['sentence'] = update_file.index
print(len(update_file))

assert len(update_file) >= len(pred_result), 'Error'
update_file = update_file.merge(pred_result, how='left', on='sentence')

update_file = update_file[['title_orig', 'word', 'word_li']]
update_file.columns = ['title', y_pred_col, 'word_li']


# In[ ]:


# Check
chk_merge = update_file[~update_file['name_pred'].isna()].reset_index(drop=True)
for i in range(len(chk_merge)):
    
    cur_word = chk_merge.loc[i, 'word_li'][0]
    cur_title = chk_merge.loc[i, 'title']
    
    if cur_word not in cur_title:
        print(i, cur_word, cur_title)
        


# In[ ]:


update_file[~update_file['name_pred'].isna()]
# update_file


# In[ ]:


# update_file[~update_file['name_pred'].isna()]
pred_result


# In[ ]:


# Console
update_file[update_file.index<=20]
# pred_result[pred_result['sentence']==13]
# pred_result
# update_file


# In[ ]:


# update_file[~update_file['name_pred'].isna()]
update_file[update_file.index==13]['title'].values


# In[ ]:


if y_pred_col in data_raw.columns:
    data_raw = data_raw.drop(y_pred_col, axis=1)

update_file = data_raw.merge(update_file, how='left', on='title')
update_file = update_file.drop('title_orig', axis=1)

update_file = update_file.reset_index(drop=True)
update_file['index'] = update_file.index

update_file.to_excel(data_file, index=False, encoding='utf-8-sig')


# In[ ]:


update_file


# ## Let's check what classifier learned

# In[ ]:


from collections import Counter
info = tagger.info()

def print_transitions(trans_features):
    for (label_from, label_to), weight in trans_features:
        print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))

print("Top likely transitions:")
print_transitions(Counter(info.transitions).most_common(15))

print("\nTop unlikely transitions:")
print_transitions(Counter(info.transitions).most_common()[-15:])


# We can see that, for example, it is very likely that the beginning of an organization name (B-ORG) will be followed by a token inside organization name (I-ORG), but transitions to I-ORG from tokens with other labels are penalized. Also note I-PER -> B-LOC transition: a positive weight means that model thinks that a person name is often followed by a location.
# 
# Check the state features:

# In[ ]:


def print_state_features(state_features):
    for (attr, label), weight in state_features:
        print("%0.6f %-6s %s" % (weight, label, attr))    

print("Top positive:")
print_state_features(Counter(info.state_features).most_common(20))

print("\nTop negative:")
print_state_features(Counter(info.state_features).most_common()[-20:])


# ## Word2Vec

# In[ ]:


import gensim
from gensim import matutils
from gensim.models.word2vec import Word2Vec

model = gensim.models.KeyedVectors.load_word2vec_format(
        path_resource + '/tmunlp_1.6B_WB_50dim_2020v1.bin.gz', 
        unicode_errors='ignore',
        binary=True
    )


# In[ ]:


# Method 1

# wv_data = word_sentence_list
wv_data = word_sentence_list[0]

result = pd.DataFrame()

for i in range(len(wv_data)):

    word_vec = {}
    for w in word_sentence_list[i]:
        try:
            word_vec[w] = model.get_vector(w)
        except:
            pass

    # Create DF
    keys = list(word_vec.keys())
    vec_df = pd.DataFrame({'word':keys,
                          'index':range(len(keys))})

    vec_df = cbyz.df_cross_join(vec_df, vec_df)
    vec_df = vec_df[vec_df['index_x']<vec_df['index_y']]             .reset_index(drop=True) 
    
    for j in range(len(vec_df)):
        vec1 = model.get_vector(vec_df.loc[j, 'word_x'])
        vec2 = model.get_vector(vec_df.loc[j, 'word_y'])
        similarity = np.dot(matutils.unitvec(vec1), matutils.unitvec(vec2))
        vec_df.loc[j, 'similarity'] = similarity

    result = result.append(vec_df)
    
    if i % 500 == 0:
        print(i, '/', len(word_sentence_list))
    
result = result.reset_index(drop=True)


# In[ ]:


# Method 2

wv_data = word_sentence_list
# wv_data = word_sentence_list[0]

result = pd.DataFrame()

for i in range(len(wv_data)):

    word_vec = {}
    for w in word_sentence_list[i]:
        try:
            word_vec[w] = model.get_vector(w)
        except:
            pass

    # Create DF
    keys = list(word_vec.keys())
    vec_df = pd.DataFrame({'word':keys,
                          'index':range(len(keys))})

    for j in range(1, len(vec_df)):
        vec1 = model.get_vector(vec_df.loc[j, 'word'])
        vec2 = model.get_vector(vec_df.loc[j-1, 'word'])
        similarity = np.dot(matutils.unitvec(vec1), matutils.unitvec(vec2))
        vec_df.loc[j, 'similarity'] = similarity

    result = result.append(vec_df)
    
    if i % 500 == 0:
        print(i, '/', len(word_sentence_list))
    
result = result.reset_index(drop=True)


# In[ ]:


word_sentence_list[0]


# In[ ]:


result.to_excel(path_export + '/wv_result.xlsx', index=False, encoding='utf-8-sig')


# In[ ]:


寶格麗
馨香
浪漫
玫香
淡香精

bvlgari
寶格麗
晶澈
女性
淡香水


# In[ ]:


result


# In[ ]:


result[result['similarity']>0.5]


# In[ ]:


type(model)


# In[ ]:


# model.vectors
# model.vocab


# In[ ]:


len(model.vocab)

def master():
    
    # - 跟淡香水之間的距離
    #   和男性、女性、中性的距離
    # v0.0302
    # - 如果title中同時出現「香水」、「香精」、「古龍」兩個以上就排除
    # v0.0305
    # - Convert ipynb to py
    # v0.0306
    
    
    pass


if __name__ == '__main__':
    
    master()

