import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

# Load the dataset
df = pd.read_csv('allergy_detection_data.csv')

# Encode categorical columns
label_encoders = {}
for col in ['Main Symptom', 'Affected Areas', 'Sub-Allergy Type']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Define features and target
X = df[['Grayscale Value', 'Redness Value', 'Main Symptom', 'Affected Areas', 'Sub-Allergy Type']]
y = df[['Allergy Type', 'Allergy Item']]

# Split dataset into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the RandomForestClassifier model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate accuracy for each target
accuracy_allergy_type = accuracy_score(y_test['Allergy Type'], y_pred[:, 0])
accuracy_allergy_item = accuracy_score(y_test['Allergy Item'], y_pred[:, 1])

print("Accuracy for Allergy Type:", accuracy_allergy_type)
print("Accuracy for Allergy Item:", accuracy_allergy_item)

# Save the trained model and label encoders
joblib.dump(model, 'allergy_model.pkl')
for name, le in label_encoders.items():
    joblib.dump(le, f'{name}_encoder.pkl')

print("Model and encoders saved successfully.")
