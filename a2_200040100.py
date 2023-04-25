# -*- coding: utf-8 -*-
"""A2_200040100.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wbQG1mTms8ia85Q4aMm5ImRdrHWuTpUQ

# **# EE 769 : Programming Assigmnet -2**
"""

# Data augmentation and normalization for training
# Just normalization for validation
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

data_dir = '/content/drive/MyDrive/hymenoptera_data/hymenoptera_data'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x])
                  for x in ['train', 'val']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,
                                             shuffle=True, num_workers=2)
              for x in ['train', 'val']}
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

"""## Classification and Feature Engineering

Name : Pooja Saini

Roll No. : 200040100

**Objective 1:** Learn various steps and due diligence needed to train successful classification models.

**Background:** Some experiments were conducted on mice to see if a treatment of Down’s syndrome works or not.Mice were divided into control and diseased (genotype), treated or untreated and whether it shows a particularbehavior or not (treatment_behavior). Readings for 77 proteins were recorded for the mice, but some of thereadings were discarded if they seemed unreliable (out of range).

1. Let your code read the data directly from https://www.ee.iitb.ac.in/~asethi/Dump/MouseTrain.csv[0]
"""

import pandas as pd

# Read the data from the URL
url = "https://www.ee.iitb.ac.in/~asethi/Dump/MouseTrain.csv"
df = pd.read_csv(url)

"""2. Perform exploratory data analysis to find out:
   
   a. Which variables are usable, and which are not?
   
   b. Are there significant correlations among variables?

   c. Are the classes balanced?


   refresence: https://www.analyticsvidhya.com/blog/2021/08/how-to-perform-exploratory-data-analysis-a-guide-for-beginners/
"""

# View the first few rows of the dataset
print(df.head())

# View the last few rows of the dataset
print(df.tail())

# View No. of rows and columns in dataset 
df.shape

# View the dataset data types
df.info()

# Check for missing values
print(df.isnull().sum())

# Examine the distributions of each variable
df.describe()

#check number of duplicate row in dataset
df.duplicated().sum()

import matplotlib.pyplot as plt
import seaborn as sns

# Calculate the correlation matrix
corr_matrix = df.corr()

# Plot the correlation matrix as a heatmap using sns.heatmap(), which help in visualize correlations between variables. 
# Darker colors indicate stronger positive correlations, 
# lighter colors indicate weaker correlations or negative correlations.
# Plot the correlation matrix as a heatmap

sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")

# Identify highly correlated variables
# Store and print the pairs of highly correlated variables and their correlation coefficients

corr_threshold = 0.9
corr_pairs = {}
for i in range(len(corr_matrix.columns)):
    for j in range(i):
        if abs(corr_matrix.iloc[i, j]) > corr_threshold:
            colname1 = corr_matrix.columns[i]
            colname2 = corr_matrix.columns[j]
            corr_pairs[(colname1, colname2)] = corr_matrix.iloc[i, j]

if corr_pairs:
    print("Highly correlated variables:")
    for pair, corr in corr_pairs.items():
        print(f"{pair}: {corr}")
else:
    print("No highly correlated variables found.")

"""3. Develop a strategy to deal with missing variables. You can choose to impute the variable. The recommendedway is to use multivariate feature imputation 

  Refrence:  https://scikit-learn.org/stable/modules/impute.html)
"""

# Use Multivariate feature imputation Method

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# Identify missing values
missing_cols = df.columns[df.isna().any()].tolist()

# Impute missing values using multivariate feature imputation
# predict missing values based on the values of other features in the dataset
imputer = IterativeImputer(random_state=0)
df_imputed = pd.DataFrame(imputer.fit_transform(df.select_dtypes(include=['float'])))

# check any missing values remain or not
print(df_imputed.isnull().sum())

df_imputed

# delete column because missing values is more than 150
# delete highly correlated columns 
df=df.dropna(axis=1)
print(df.isnull().sum())

"""5.Using five-fold cross-validation (you can use GridSearchCV from scikit-learn) to find the reasonable (I cannotsay “best” because you have two separate classifications to perform) hyper-parameter settings for thefollowing model types:

a. Linear SVM with regularization as hyperparameter

https://www.vebuso.com/2020/03/svm-hyperparameter-tuning-using-gridsearchcv/
"""

from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler


# split the data into features and labels
X = df.iloc[:, :-2]        # features
y_click = df.iloc[:, -2]  # first classification labels
y_move = df.iloc[:, -1]   # second classification labels

# scale the features

# StandardScaler transformer scales the features of a dataset to have zero mean and unit variance
scaler = StandardScaler()
#applies the transformation to the data by subtracting the mean and dividing by the standard deviation
# X_scaled matrix has same number of rows and columns as X, but the values have been transformed so that each feature has zero mean and unit variance
X_scaled = scaler.fit_transform(X)

# set up a parameter grid for the linear SVM with a range of values for the C hyperparameter
param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100]}

# perform grid search for the click classification task
click_svc = LinearSVC(loss='hinge', max_iter=100000)
click_grid_search = GridSearchCV(click_svc, param_grid, cv=5)
click_grid_search.fit(X_scaled, y_click)
print("Best hyperparameters for click classification:", click_grid_search.best_params_)

# perform grid search for the move classification task
move_svc = LinearSVC(loss='hinge', max_iter=100000)
move_grid_search = GridSearchCV(move_svc, param_grid, cv=5)
move_grid_search.fit(X_scaled, y_move)
print("Best hyperparameters for move classification:", move_grid_search.best_params_)

"""b. RBF kernel SVM with kernel width and regularization as hyperparameters

https://www.vebuso.com/2020/03/svm-hyperparameter-tuning-using-gridsearchcv/
"""

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC

# split into features and target same as part a
X = df.iloc[:, :-2]
y1 = df.iloc[:, -2]# first classification target
y2 = df.iloc[:, -1] # second classification target


# set up parameter grid for SVM
param_grid = {
    'C': [0.01,0.1, 1, 10,100],
    'gamma': [0.01, 0.1, 1, 10,100]
}

# perform five-fold cross-validation using GridSearchCV
# two separate SVM models using GridSearchCV, one for each classification task, and fit them to the data using five-fold cross-validation
svm1 = GridSearchCV(SVC(kernel='rbf'), param_grid, cv=5)
svm2 = GridSearchCV(SVC(kernel='rbf'), param_grid, cv=5)

svm1.fit(X, y1)
svm2.fit(X, y2)

# print best hyperparameters for each model
print("Best hyperparameters for y1: ", svm1.best_params_)
print("Best hyperparameters for y2: ", svm2.best_params_)

"""c. Neural network with single ReLU hidden layer and Softmax output (hyperparameters: number ofneurons, weight decay)

https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html
"""

import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler


# separate the features and target sample as above two parts of question no. 5
X = df.iloc[:, :-2]
y1 = df.iloc[:, -2] # first classification target
y2 = df.iloc[:, -1] # second classification target

# standardize the features same as a.) part of question 5
scaler = StandardScaler()
X = scaler.fit_transform(X)

# define the classifier
# MLPClassifier trains iteratively at each time step the partial derivatives of the loss function with respect to the model parameters are computed to update the parameters.
# Activation function for the hidden layer and ‘relu’, the rectified linear unit function, returns f(x) = max(0, x)
# The solver for weight optimization and ‘adam’ refers to a stochastic gradient-based optimizer
# random number generation for weights and bias initialization
clf = MLPClassifier(activation='relu', solver='adam', random_state=42)

# define the hyperparameters to be tuned
# number of neurons in the ith hidden layer
# alpha : Strength of the L2 regularization term
param_grid = {
              'hidden_layer_sizes': [(10,), (50,), (100,)],
              'alpha': [0.0001, 0.001, 0.01]
              }

# perform 5-fold cross-validation 
grid1 = GridSearchCV(clf, param_grid, cv=5)
grid2 = GridSearchCV(clf, param_grid, cv=5)
grid1.fit(X, y1)
grid2.fit(X, y2)


print("Best hyperparameters for target 1:", grid1.best_params_)
print("Best hyperparameters for target 2:", grid2.best_params_)

"""The warning message indicates that the maximum number of iterations (200) has been reached, but the optimization process has not yet converged to a solution that meets the desired convergence criteria. This can happen because the neural network is too complex, the training data is noisy, or the learning rate is too high. If the algorithm has not converged after the maximum number of iterations, the weights of the neural network will be returned, but they may not represent the best solution

d. Random forest (max tree depth, max number of variables per node)

https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold

# Split data into features and target
X = df.iloc[:, 0:-2]
y_1 = df.iloc[:, -2]  # first classification target
y_2 = df.iloc[:, -1] # second classification target

# Set up parameter grid to search
# 'max_depth' is maximum depth of the tree
# 'max_features' is number of features to consider when looking for the best split
param_grid = {
    'max_depth': [2, 4, 6, 8],
    'max_features': ['sqrt', 'log2', None],
}

# Create random forest classifier
# n_estimatorsint, default=100 is number of trees in the forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# Perform grid search with cross-validation
# n_jobs is the number of jobs to run in parallel
# verboseint, default=0 is Controls the verbosity when fitting and predicting.
grid_search1 = GridSearchCV(rf,param_grid,cv=5,n_jobs=-1,verbose=1)
grid_search2 = GridSearchCV(rf,param_grid,cv=5,n_jobs=-1,verbose=1)

# Fit the grid search to the data
grid_search1.fit(X, y_1)
grid_search2.fit(X, y_2)

# Print the best hyperparameters
print("Best hyperparameters for classification 1: ", grid_search1.best_params_)
print("Best hyperparameters for classification 2: ", grid_search2.best_params_)

"""6. Check feature importance for each model to see if the same proteins are important for each model. Read upon how to find feature importance.

 refrence : https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html

 For solving error: copy these lines from chat gpt

            le = LabelEncoder()
            y__1 = le.fit_transform(y__1)
            y__2 = le.fit_transform(y__2) 
"""

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder


# Split the data into features and labels
X = df.iloc[:, :-2]
y__1 = df.iloc[:, -2]
y__2 = df.iloc[:, -1]


# Train a Random Forest model and compute feature importance for classification 1
# print in ascending order

rf_1 = RandomForestClassifier(n_estimators=100, random_state=42)
rf_1.fit(X, y__1)
rf1_feature_importances = pd.DataFrame(rf_1.feature_importances_, index=X.columns, columns=['importance'])
rf1_feature_importances = rf1_feature_importances.sort_values('importance', ascending=False)
print('Random Forest feature importance for classification 1:\n ', rf1_feature_importances)


# Train a Random Forest model and compute feature importance for classification 2
# print in ascending order

rf_2 = RandomForestClassifier(n_estimators=100, random_state=42)
rf_2.fit(X, y__2)
rf2_feature_importances = pd.DataFrame(rf_2.feature_importances_, index=X.columns, columns=['importance'])
rf2_feature_importances = rf2_feature_importances.sort_values('importance', ascending=False)
print('Random Forest feature importance for classification 2:\n', rf2_feature_importances)


# Encode the string labels to numerical values

le = LabelEncoder()
y__1 = le.fit_transform(y__1)
y__2 = le.fit_transform(y__2)

# Train an XGBoost model and compute feature importance for classification 1

xgb1 = XGBClassifier(n_estimators=100, random_state=42)
xgb1.fit(X, y__1)
xgb1_feature_importances = pd.DataFrame(xgb1.feature_importances_, index=X.columns, columns=['importance'])
xgb1_feature_importances = xgb1_feature_importances.sort_values('importance', ascending=False)
print('XGBoost feature importance for classification 1:\n', xgb1_feature_importances)


# Train an XGBoost model and compute feature importance for classification 2

xgb2 = XGBClassifier(n_estimators=100, random_state=42)
xgb2.fit(X, y__2)
xgb2_feature_importances = pd.DataFrame(xgb2.feature_importances_, index=X.columns, columns=['importance'])
xgb2_feature_importances = xgb2_feature_importances.sort_values('importance', ascending=False)
print('XGBoost feature importance for classification 2:\n', xgb2_feature_importances)

# for classification 1 ,Compare the two models by printing the top 10 most important features for each 
rf1_top10 = rf1_feature_importances.head(10).index.tolist()
xgb1_top10 = xgb1_feature_importances.head(10).index.tolist()
common_features1 = set(rf1_top10).intersection(set(xgb1_top10))
print('Common top 10 important features for classification 1:', common_features1)

# for classification 2 ,Compare the two models by printing the top 10 most important features for each 
rf2_top10 = rf2_feature_importances.head(10).index.tolist()
xgb2_top10 = xgb2_feature_importances.head(10).index.tolist()
common_features2 = set(rf2_top10).intersection(set(xgb2_top10))
print('Common top 10 important features for classification 2:', common_features2)

"""7. See if removing some features systematically will improve your models (e.g. using recursive featureelimination 

    https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.RFECV.html).
"""

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFECV
from sklearn.preprocessing import StandardScaler


# Separate the features and the target variable
X = df.iloc[:, :-2]
_y1 = df.iloc[:, -2]  # for classification 1
_y2 = df.iloc[:, -1]  # for classification 2

# Split the data into training and testing sets

X1_train, X1_test, y1_train, y1_test = train_test_split(X, _y1, test_size=0.2, random_state=42) # for classification 1
X2_train, X2_test, y2_train, y2_test = train_test_split(X, _y2, test_size=0.2, random_state=42) # for classification 2

# Preprocess the data by standardizing the features


scaler = StandardScaler()
X1_train_scaled = scaler.fit_transform(X1_train)  # for classification 1
X1_test_scaled = scaler.transform(X1_test)

X2_train_scaled = scaler.fit_transform(X2_train)   # for classification 2
X2_test_scaled = scaler.transform(X2_test)

# Create a logistic regression model

lr1 = LogisticRegression(max_iter=1000)  # for classification 1
lr2 = LogisticRegression(max_iter=1000)  # for classification 2

# Apply recursive feature elimination with cross-validation

selector1 = RFECV(lr1, cv=5)                      # for classification 1 
selector1.fit(X1_train_scaled, y1_train)

selector2 = RFECV(lr2, cv=5)                     # for classification 2
selector2.fit(X2_train_scaled, y2_train)

# Print the selected features and their rankings

selected_features1 = X1_train.columns[selector1.support_]    # for classification 1 
feature_rankings1 = selector1.ranking_ 
print("Selected features:", selected_features1)
print("Feature rankings:", feature_rankings1)

selected_features2 = X2_train.columns[selector2.support_]    # for classification 2 
feature_rankings2 = selector2.ranking_ 
print("Selected features:", selected_features2)
print("Feature rankings:", feature_rankings2)

# Evaluate the model on the testing set

X1_test_selected = X1_test[selected_features1]   # for classification 1 
lr1.fit(X1_test_selected, y1_test)
accuracy1 = lr1.score(X1_test_selected, y1_test)
print("Accuracy for classification 1 :", accuracy1)

X2_test_selected = X2_test[selected_features2]   # for classification 2 
lr2.fit(X2_test_selected, y2_test)
accuracy2 = lr2.score(X2_test_selected, y2_test)
print("Accuracy for classification 2 :", accuracy2)

"""8. Finally, test a few promising models on the test data:
https://www.ee.iitb.ac.in/~asethi/Dump/MouseTest.csv 

  Refrence : https://scikit-learn.org/stable/modules/preprocessing.html
"""

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# Read the testing data
test_url = "https://www.ee.iitb.ac.in/~asethi/Dump/MouseTest.csv"
test_df = pd.read_csv(test_url)

# Separate the features and the target variable
X_train = df.iloc[:, :-2]
y_train = df.iloc[:, -2]
X_test = test_df.iloc[:, :-2]
y_test = test_df.iloc[:, -2]

# Make sure the column names of X_test match those of X_train
X_test = X_test[X_train.columns]

# Scale the data using standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train and test a logistic regression model
lr = LogisticRegression(max_iter=1000)
lr.fit(X_train_scaled, y_train)
y_pred_lr = lr.predict(X_test_scaled)
accuracy_lr = accuracy_score(y_test, y_pred_lr)
print("Logistic Regression Accuracy:", accuracy_lr)

# Train and test a random forest model
rf = RandomForestClassifier()
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
accuracy_rf = accuracy_score(y_test, y_pred_rf)
print("Random Forest Accuracy:", accuracy_rf)

# Train and test a support vector machine model
svc = SVC()
svc.fit(X_train, y_train)
y_pred_svc = svc.predict(X_test)
accuracy_svc = accuracy_score(y_test, y_pred_svc)
print("SVM Accuracy:", accuracy_svc)

"""9. Read the pytorch tutorial to use a pre-trained “ConvNet as fixed feature extractor” fromhttps://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html and you can ignore “finetuning theConvNet”. Test this code out to see if it runs properly in your environment after eliminating code blocks thatyou do not need."""

# License: BSD
# Author: Sasank Chilamkurthy

from __future__ import print_function, division

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import torch.backends.cudnn as cudnn
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import time
import os
import copy

cudnn.benchmark = True
plt.ion()   # interactive mode

#training the model
def train_model(model, criterion, optimizer, scheduler, num_epochs=25):
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs - 1}')
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

        print()

    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'Best val Acc: {best_acc:4f}')

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model

#copy from chat gpt to avoid error
import warnings
warnings.filterwarnings("ignore", message="The parameter 'pretrained' is deprecated since 0.13 and may be removed in the future, please use 'weights' instead.")
warnings.filterwarnings("ignore", message="Arguments other than a weight enum or `None` for 'weights' are deprecated since 0.13 and may be removed in the future.")

#convNet as fixed feautre extractor
model_conv = torchvision.models.resnet18(pretrained=True)
for param in model_conv.parameters():
    param.requires_grad = False

# Parameters of newly constructed modules have requires_grad=True by default
num_ftrs = model_conv.fc.in_features
model_conv.fc = nn.Linear(num_ftrs, 2)

model_conv = model_conv.to(device)

criterion = nn.CrossEntropyLoss()

# Observe that only parameters of final layer are being optimized as
# opposed to before.
optimizer_conv = optim.SGD(model_conv.fc.parameters(), lr=0.001, momentum=0.9)

# Decay LR by a factor of 0.1 every 7 epochs
exp_lr_scheduler = lr_scheduler.StepLR(optimizer_conv, step_size=7, gamma=0.1)

#training and evaluation
model_conv = train_model(model_conv, criterion, optimizer_conv,
                         exp_lr_scheduler, num_epochs=25)

"""10. Write a function that outputs ResNet18 features for a given input image. Extract features for training images(in image_datasets['train']). You should get an Nx512 dimensional array.


refrence : chAT GPT
"""

import torch
import torchvision.models as models
import torchvision.transforms as transforms

def get_resnet18_features(image):
    # Load the ResNet18 model with pretrained weights
    resnet18 = models.resnet18(pretrained=True)
    
    # Remove the last layer (classifier) from the ResNet18 model
    resnet18 = torch.nn.Sequential(*list(resnet18.children())[:-1])
    
    # Set the ResNet18 model to evaluation mode
    resnet18.eval()
    
    # Define the image transformations
    data_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    
    # Apply the image transformations to the input image
    input_tensor = data_transforms(image)
    input_tensor = input_tensor.unsqueeze(0)
    
    # Generate the ResNet18 features for the input image
    with torch.no_grad():
        features = resnet18(input_tensor)
        
    # Flatten the features into a 1D tensor
    features = torch.flatten(features)
    
    return features

"""the input to the get_resnet18_features function is a PyTorch tensor instead of a PIL Image or NumPy array. To fix this, we need to convert the input tensor to a PIL Image before passing it to the ResNet18 model"""

from torchvision import transforms

# Define transform to convert tensor to PIL image
tensor_to_pil = transforms.ToPILImage()

# Extract ResNet18 features for training images

## Extract ResNet18 features for training images
train_features = []
for inputs, labels in  dataloaders['train']:
    for input in inputs:
        input_image = tensor_to_pil(input)
        features = get_resnet18_features(input_image)
        train_features.append(features.numpy())
train_features = np.array(train_features)

"""11. Compare L2 regularized logistic regression, RBF kernel SVM (do grid search on kernel width andregularization), and random forest (do grid search on max depth and number of trees). Test the final modelon test data and show the results -- accuracy and F1 score.

12. Summarize your findings and write your references.

# Objective 1: 

Data preparation: for successful classification model we need to prepare the data. This includes identifying the relevant variables,handle missing values, cleaning and transforming the data, and splitting the data into training and testing sets.

Feature engineering: Feature engineering involves selecting the most important variables for the model, reducing dimensionality, and creating new features based on domain knowledge.

Model selection:There are various types of classification algorithms such as decision trees, logistic regression, random forests, support vector machines, and neural networks, among others we need to choice best.

Model training and evaluation: Once the model is selected, it needs to be trained on the training data and evaluated on the testing data to ensure that the model is not overfitting or underfitting the data.

Hyperparameter tuning: Hyperparameters are the parameters that are set before the model training, and they have a significant impact on the model's performance. Hyperparameter tuning involves adjusting these parameters to optimize the model's performance.

# Objective 2:
Pre-trained neural networks can be effectively used to extract domain-specific features for new tasks. These networks, which have been trained on vast amounts of data, can be fine-tuned on a smaller dataset to learn specific features relevant to the new task. This approach can save significant time and resources compared to training a new network from scratch.

One popular application of pre-trained networks is transfer learning, where the learned features from one task are used to improve performance on a related task. Another application is feature extraction, where the pre-trained network is used to extract features from new data, which are then fed into a separate classifier.
"""