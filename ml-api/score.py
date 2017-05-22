from sklearn.ensemble import RandomForestClassifier
from numpy import genfromtxt, savetxt

class HelthRandomForest(object):

    def __init__(self, **kargs):
        self.kargs = kargs

    def training(self):
        '''
            Se existe já arquivo de treino...
        '''
        treined = True

        if not treined:
            print("trainning...")
            #create the training & test sets, skipping the header row with [1:]
            dataset = genfromtxt(open('data/train.csv','r'), delimiter=',', dtype='f8')[1:]
            target = [x[0] for x in dataset]
            train = [x[1:] for x in dataset]
            test = genfromtxt(open('data/test.csv','r'), delimiter=',', dtype='f8')[1:]
            #create and train the random forest
            #multi-core CPUs can use: rf = RandomForestClassifier(n_estimators=100, n_jobs=2)
            rf = RandomForestClassifier(n_estimators=100)
            rf.fit(train, target)
            savetxt('data/submission2.csv', rf.predict(test), delimiter=',', fmt='%f')
        return treined

    def get_score(self):
        print("Getting score...")
        #rf = RandomForestClassifier(n_estimators=100)
        ## Metodos para retorno...
        return 0.55
