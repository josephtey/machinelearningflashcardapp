import pandas as pd
import numpy as np
import csv
import pickle
import argparse
import math

from lentil import datatools
from lentil import models
import filterdata
from operator import itemgetter
import constants

def savePickle(item, fname):
    with open(fname, 'wb') as handle:
        pickle.dump(item, handle, protocol=pickle.HIGHEST_PROTOCOL)

def loadPickle(fname):
    with open(fname, 'rb') as handle:
        item = pickle.load(handle)
    return item
    
def mnemosyneToTextfile(input_file, output_file):
    with open(input_file, 'rb') as f:
        history = pickle.load(f).data
    
    columns = ['user_id','timestamp','module_id','outcome']
    file = open(output_file, 'w')
    file.write(','.join(columns)+'\n')
    for i in range(len(history)):
        print str(i) + ' out of ' + str(len(history))
        line = ''
        for x in range(len(columns)):
            line = line + str(history.iloc[i][columns[x]])
            if x != (len(columns)-1):
                line += ","
                
        file.write(line + '\n')

def textToInteractionHistory(fname, timestamp, user_id, item_id, outcome, correct):
    data = []
    cols = ['outcome', 'timestamp','time_elapsed','student_id', 'module_id','module_type','timestep'] + constants.FEATURE_NAMES
    f = open(fname, 'rb')

    reader = csv.DictReader(f)
    for i, row in enumerate(reader): 
        temp = []
        p = False
        if row[outcome] == correct:
            p = True
        else:
            p = False
        temp.append(p)
        temp.append(int(row[timestamp]))
        temp.append(int(row['time_elapsed']))        
        temp.append(row[user_id])
        temp.append(row[item_id])
        temp.append('assessment')
        temp.append(int(row['history_correct'])+int(row['history_wrong']))
        for x in range(len(constants.FEATURE_NAMES)):
            temp.append(row[constants.FEATURE_NAMES[x]])

        data.append(temp)

    df = pd.DataFrame(columns = cols, data = data).drop_duplicates()
    ih = datatools.InteractionHistory(df)

    return ih

def filterFromArray(index, df):
    cols = ['outcome','timestamp','time_elapsed', 'student_id', 'module_id','module_type','timestep'] + constants.FEATURE_NAMES + ['time_since_previous_interaction','duration']
    
    filtered = pd.DataFrame(columns=cols)
    
    def comboIsInIndex(combo):
        x = False
        for i in range(len(index)):
            if index[i] == combo:
                x = True
                break;
        return x
    
    for i in range(len(df)):  
        if i % 1000 == 0:
            print str(i) +' out of ' + str(len(df))
        combo = (df.iloc[i]['student_id'], df.iloc[i]['module_id'])
        if comboIsInIndex(combo) == True:
            filtered = filtered.append(df.iloc[i])
            
    return filtered

def filteredFromHistory(history):
    index = list(map(itemgetter(0), filterdata.getData(history).items()))
    return index

def filterHistory(df):
    filtered = datatools.InteractionHistory(filterFromArray(filteredFromHistory(df), df))
    return filtered

def splitHistory(ih, split):
    #get interaction history
    splitPoint = int(round((float(ih.num_students())/100.0)*float(split)))
    
    train_df = ih.data[ih.data['student_id'].astype(int) <= splitPoint]
    test_df = ih.data[ih.data['student_id'].astype(int) > splitPoint]

    return datatools.InteractionHistory(train_df), datatools.InteractionHistory(test_df)
    
def sigmoid(x):
      return 1 / (1 + math.exp(-x))

def getTrueFalseDistribution(df):
    data = list(df['outcome'])
    data = [int(i) for i in data]
    return 'True/Total: ' + str(float(sum(data))/float(len(data)))

def getPropertiesOfData(ih, data_name):
    print data_name
    print str(ih.num_students()) + ' students'
    print str(ih.num_assessments()) + ' assessments'
    print str(len(ih.data)) + ' interactions'
    print getTrueFalseDistribution(ih.data) + '\n'


