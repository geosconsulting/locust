import pandas as pd
import math
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt

# https://sefiks.com/2021/01/06/feature-importance-in-logistic-regression/

feature_names = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

x, y = load_iris(return_X_y=True)
df = pd.DataFrame(x, columns=feature_names)
df['target'] = y
print(df.head())

#0: setosa, 1: versicolor, 2: virginica
df = df[df['target'] != 2]

for feature_name in feature_names:
    df[feature_name] = df[feature_name] / df[feature_name].std()

model = LogisticRegression(random_state=0).fit(df[feature_names].values,
                                               df['target'].values)

score = model.score(df[feature_names].values, df['target'].values)
print(score)

w0 = model.intercept_[0]
w = w1, w2, w3, w4 = model.coef_[0]

equation = "y = %f + (%f * x1) + (%f * x2) + (%f * x3) + (%f * x4)" % \
           (w0, w1, w2, w3, w4)
print(equation)

idx = 99
x = df.iloc[idx][feature_names].values
y = model.predict_proba(x.reshape(1, -1))[0]
print(y[1])


def sigmoid(x):
    return 1 / (1 + pow(math.e, -x))


result = 0
result += w0
for i in range(0, 4):
    result += x[i] * w[i]
result = sigmoid(result)
print(result)

feature_importance = pd.DataFrame(feature_names, columns=["feature"])
feature_importance["importance"] = pow(math.e, w)
feature_importance = feature_importance.sort_values(by=["importance"], ascending=False)


ax = feature_importance.plot.barh(x='feature', y='importance')
plt.show()