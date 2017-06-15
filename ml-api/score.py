import sklearn as sk
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report, confusion_matrix
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os.path
import logging

log = logging.getLogger(__name__)

class HelthCholesterol(object):
    def __init__(self, base, pkl_file):
        self.pkl_file = pkl_file
        self.base = base
        if not os.path.exists(self.pkl_file):
            logging.info("Treinando a base....")
            self.training(self.base, self.pkl_file)
        else:
            logging.info("Arquivo pkf existe")

    '''
    Para uso na regressão linear com SGD (Stochastic Gradient Descent),
    um algoritmo popular de treinamento de uma grande variedade de modelos de aprendizado de máquina.
    O StandardScaler é usado para dimensionar os recursos de acordo com a variação de unidade.
    O dimensionamento de recursos, também conhecido como normalização de dados, faz com que recursos (features)
    com valores amplamente distribuídos não tenham peso excessivo na função objetiva.

    Normaliza as features para regreção linear with withStd 0.
    '''

    def fit_standardbase(self, X_train, X_test):
        try:
            scaler = StandardScaler()
            scaler.fit(X_train)
            X_train = scaler.transform(X_train)
            X_test = scaler.transform(X_test)
            return X_train, X_test
        except Exception as e:
            logging.debug("Erro no fit_standardbase")

    '''
        Gera um png das relevancias de features e salva em log
    '''

    def top_features(self, features_list, clf_feature_importances):
        feature_importance = clf_feature_importances
        # make importances relative to max importance
        feature_importance = 100.0 * (feature_importance / feature_importance.max())
        sorted_idx = np.argsort(feature_importance)
        newlist = [i for i, _ in enumerate(list(feature_importance))]
        print("TOP Features:")
        feature_string = "a"
        for i in reversed(newlist):
            feature_string += "features {0}, {1} \n".format(sorted_idx[i], features_list[sorted_idx[i]])

        print(feature_string)

        # Save image
        pos = np.arange(sorted_idx.shape[0]) + 0.5
        plt.subplot(1, 2, 2)
        fig = plt.figure(1, figsize=(1000, 1000))
        ax = fig.add_subplot(111)
        plt.barh(pos, feature_importance[sorted_idx], align='center')
        plt.yticks(pos, map(lambda x: features_list[x], sorted_idx))
        plt.xlabel('TOP Features')
        plt.title('Top Features')
        fig.savefig('features_relevance.png')  # save the figure to file
        return True

    # Testa o modelo
    def test_model(self, X_test, clf):
        try:
            predictions = clf.predict(X_test)
            probs = clf.predict_proba(X_test)
            auc_ = roc_auc_score(y_test, probs[:, 1])
            logging.info("AUC: %.4f" % auc_)
            logging.info("acurácia: %.4f" % accuracy_score(y_test, predictions))
            logging.info(confusion_matrix(y_test, predictions))
            logging.info(classification_report(y_test, predictions))
            return True
        except Exception as e:
            logging.debug("Erro no teste do modelo...")

    # Criacao da arvore
    def create_rndclf(self, X_train, y_train):
        clf = RandomForestClassifier(n_jobs=300)
        clf.fit(X_train, y_train)
        return clf

    def training(self, base, pkl_file):
        try:
            base = pd.read_csv(base, ";")
            print(">> Removendo a coluna colesterol")
            features = base.columns.tolist()
            features.pop(features.index('Colesterol'))

            print(">> Treinando a base para identificar pessoas que poderão ter problemas com colesterol elevado.")
            X = base[features]  # MATRIZ X COM AS FEATURES
            y = base.Colesterol  # VETOR Y COM AS RESPOSTAS

            print(">> Quebrando a base entre Treino e Teste ")
            print("Pos Debug")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            print("Base train_test_split")

            print(">> Padronizando a base (FIT)")
            X_train, X_test = self.fit_standardbase(X_train, X_test)

            print(" Criando o modelo... ")
            clf = self.create_rndclf(X_train, y_train)

            print(" Testando a base, incluíndo validação das feaatures importantes")
            self.test_model(X_test, clf)

            print("Identificando top features")
            self.top_features(features, clf.feature_importances_)

            print(" Salvando o modelo para ser utilizado... ")
            joblib.dump(clf, pkl_file)
        except Exception as e:
            print(e)

    def score(self, **weigth_data):
        value = [
            weigth_data["sexo"],
            weigth_data["horotadia"],
            weigth_data["frutadia"],
            weigth_data["carnegordura"],
            weigth_data["atividade"],
            weigth_data["hiptertensao"],
            weigth_data["diabetes"]
        ]
        clf = joblib.load(self.pkl_file)
        data = clf.predict_proba(list(value)).tolist()[0]
        return data[0]