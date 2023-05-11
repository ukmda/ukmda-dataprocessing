# python script to prep data for machine learning
# Copyright (C) Mark McIntyre
#

import pandas as pd
import os
import datetime
from sklearn.model_selection import train_test_split
from keras.models import Sequential, load_model
from keras.layers import Dense
import matplotlib.pyplot as plt


"""
For the ML routine we're going to prepare a dataset containing 
[timestamp, max_bri, avg_bri, stddev_bri, num_within_10s, mag, intersting_yn]
brightnesses will be normalised by dividing by (1280 x 720 x 255)

initially, mag will be used as a proxy for interesting
We'll split the data into cols 1-5 for features and col 6 or 7 as label.
We'll use 70% of the data to train, 15% to validate and 15% to test.

"""

IMGSIZE=1280*720*255


def isfb(x):
    if x < -3.5: 
        return 1
    return 0


def loadOneFile(dtstr, datadir):
    fname = os.path.join(datadir, f'matcheddata-{dtstr}.csv')
    if not os.path.isfile(fname):
        return None, None
    df =pd.read_csv(fname, index_col=0)
    df.drop(columns=['ExpiryDate','camid','sds','CaptureNight', 'ffname'])
    df = df.dropna()
    df['Dtstamp'] = [datetime.datetime.utcfromtimestamp(tt) for tt in df.Timestamp]
    df = df.sort_values(by=['Timestamp'])
    df2=df.set_index('Dtstamp')
    df2['num']=df2.rolling('10s').Timestamp.count()    
    df2['fireball'] = [isfb(m) for m in df2.Mag]
    df2.bmax = df2.bmax/IMGSIZE
    df2.bave = df2.bave/IMGSIZE
    df2.bstd = df2.bstd/IMGSIZE
    features = df2[['bmax','bave','bstd','num']]
    labels = df2[['fireball']]
    return features, labels


def loadDateRange(dtstr1, dtstr2, datadir):
    d1 = datetime.datetime.strptime(dtstr1, '%Y%m%d')
    d2 = datetime.datetime.strptime(dtstr2, '%Y%m%d')
    features = None
    labels = None
    while d1 <= d2:
        feat, lab = loadOneFile(d1.strftime('%Y%m%d'), datadir)
        if feat is not None:
            if features is None:
                features = feat
                labels = lab
            else:
                features = pd.concat([features, feat])
                labels = pd.concat([labels, lab])
        d1 += datetime.timedelta(days=1)
    return features, labels


def trainModel(features, labels, datadir):
    X_train, X_val_and_test, Y_train, Y_val_and_test = train_test_split(features, labels, test_size=0.3)
    X_val, X_test, Y_val, Y_test = train_test_split(X_val_and_test, Y_val_and_test, test_size=0.5)
    input_width=len(features.columns)
    model = Sequential([
        Dense(32, activation='relu', input_shape=(input_width,)),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid'),])
    model.compile(optimizer='sgd',
                loss='binary_crossentropy',
                metrics=['accuracy'])
    hist = model.fit(X_train, Y_train,
            batch_size=16, epochs=10,
            validation_data=(X_val, Y_val))
    model.evaluate(X_test, Y_test)
    plt.plot(hist.history['loss'])
    plt.plot(hist.history['val_loss'])
    plt.show()
    model.save(os.path.join(datadir, 'mymodel'))


def reuseModel(datestr, datestr2, datadir, mdlname='mymodel'):
    model = load_model(os.path.join(datadir, mdlname))
    if datestr2 is not None:
        feat, lab = loadDateRange(datestr, datestr2, datadir)
    else:
        feat, lab = loadOneFile(datestr, datadir)
    model.evaluate(feat, lab)
    pred = model.predict(feat)
    
    print(f' there were {len(lab[lab.fireball==1])} labelled fireballs')
    print(f' there were {len([p for p in pred if p > 0.9])} predicted fireballs')
    print(f' there were {len(lab)} total detections')
    #print(pred, lab)
#    for f, l in zip(pred, lab):
#        print(f, l)


if __name__ == '__main__':
    datadir = 'e:/dev/meteorhunting/testing/brightness_tests'
    datestr = '20230424'
    datestr2 = '20230501'
    reuseModel(datestr, datestr2, datadir)
