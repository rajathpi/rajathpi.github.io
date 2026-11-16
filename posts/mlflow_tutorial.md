---
title: Installing and Using MLFlow
description: Installing and Using MLFlow
meta: January 2025 · notebook
date: 2025-01
topic: Notes
list: MLflow
archived: yes
---

To install **MLFlow**, use the following command in your terminal:

```
pip install mlflow
```

Ensure that you have Python and pip installed on your system before running the command. You can verify the installation with:

```
mlflow --version
```

To view the results of your experiment, launch the **MLFlow tracking UI**:

```
mlflow ui
```

Open your browser and navigate to <http://127.0.0.1:5000>.  
You will see a dashboard where you can explore the parameters, metrics, and models from your experiment.

Take a look at the first example:  
**[First Experiment](first_experiment.html)**
