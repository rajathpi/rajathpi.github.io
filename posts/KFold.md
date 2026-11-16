---
title: K-Fold Cross-Validation
description: KFold
meta: January 2025 · notebook
date: 2025-01
topic: Notes
list: K-fold cross-validation
archived: yes
---

```
import numpy as np
from sklearn.model_selection import KFold
```

```
X = np.array([[1, 2], [3, 4], [1, 2], [3, 4]])
y = np.array([1,2,3,4])
```

```
X
```


<pre class="out">array([[1, 2],
       [3, 4],
       [1, 2],
       [3, 4]])</pre>


```
kf = KFold(n_splits=2)
kf.get_n_splits(X)
```


<pre class="out">2</pre>


```
print(kf)
```


<pre class="out">KFold(n_splits=2, random_state=None, shuffle=False)</pre>


```
for i, (train_index, test_index) in enumerate(kf.split(X)):
    print(f"Fold {i}:")
    print(f"  Train: index={train_index}")
    print(f"  Test:  index={test_index}")
```


<pre class="out">Fold 0:
  Train: index=[2 3]
  Test:  index=[0 1]
Fold 1:
  Train: index=[0 1]
  Test:  index=[2 3]</pre>


```
import numpy as np
from sklearn.model_selection import KFold

# Feature matrix (X): 10 data points, each with 2 features
X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10],
              [11, 12], [13, 14], [15, 16], [17, 18], [19, 20]])

# Target array (y): Labels for each data point
y = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# KFold with 5 splits
kf = KFold(n_splits=5)

# Display the splits
for i, (train_index, test_index) in enumerate(kf.split(X)):
    print(f"Fold {i}:")
    print(f"  Train: indices={train_index}, data={X[train_index]}, labels={y[train_index]}")
    print(f"  Test:  indices={test_index}, data={X[test_index]}, labels={y[test_index]}")
```


<pre class="out">Fold 0:
  Train: indices=[2 3 4 5 6 7 8 9], data=[[ 5  6]
 [ 7  8]
 [ 9 10]
 [11 12]
 [13 14]
 [15 16]
 [17 18]
 [19 20]], labels=[ 3  4  5  6  7  8  9 10]
  Test:  indices=[0 1], data=[[1 2]
 [3 4]], labels=[1 2]
Fold 1:
  Train: indices=[0 1 4 5 6 7 8 9], data=[[ 1  2]
 [ 3  4]
 [ 9 10]
 [11 12]
 [13 14]
 [15 16]
 [17 18]
 [19 20]], labels=[ 1  2  5  6  7  8  9 10]
  Test:  indices=[2 3], data=[[5 6]
 [7 8]], labels=[3 4]
Fold 2:
  Train: indices=[0 1 2 3 6 7 8 9], data=[[ 1  2]
 [ 3  4]
 [ 5  6]
 [ 7  8]
 [13 14]
 [15 16]
 [17 18]
 [19 20]], labels=[ 1  2  3  4  7  8  9 10]
  Test:  indices=[4 5], data=[[ 9 10]
 [11 12]], labels=[5 6]
Fold 3:
  Train: indices=[0 1 2 3 4 5 8 9], data=[[ 1  2]
 [ 3  4]
 [ 5  6]
 [ 7  8]
 [ 9 10]
 [11 12]
 [17 18]
 [19 20]], labels=[ 1  2  3  4  5  6  9 10]
  Test:  indices=[6 7], data=[[13 14]
 [15 16]], labels=[7 8]
Fold 4:
  Train: indices=[0 1 2 3 4 5 6 7], data=[[ 1  2]
 [ 3  4]
 [ 5  6]
 [ 7  8]
 [ 9 10]
 [11 12]
 [13 14]
 [15 16]], labels=[1 2 3 4 5 6 7 8]
  Test:  indices=[8 9], data=[[17 18]
 [19 20]], labels=[ 9 10]</pre>

