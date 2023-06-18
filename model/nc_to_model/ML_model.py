import pandas as pd
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from constants import *


# Read the merged dataset
merged_df = pd.read_csv(DATApath)

# Split the dataset into training and testing sets
train_df, test_df = train_test_split(merged_df, test_size=0.2, random_state=42)

# Fit the mixed linear effects model on the training set
model_formula = 'pm10 ~ AOD + RH + WS + EL + HD + WBD'
# model = smf.mixedlm(model_formula, data=train_df, groups=train_df['x'].astype(str) + '_' + train_df['y'].astype(str))
model = smf.mixedlm(model_formula, data=train_df, groups=train_df['LU'])
result = model.fit()

# Print the model summary for training
print("Training Summary:")
print(result.summary())

# Predict on the testing set
test_pred = result.predict(test_df)

# Compute the R-squared for testing
r2 = r2_score(test_df['pm10'], test_pred)

# Print the R-squared for testing
print("R-squared on the testing set:", r2)