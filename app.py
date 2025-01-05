import pandas as pd
import os
import numpy as np
import joblib
from flask import Flask, request, jsonify , render_template
from PIL import Image
import cv2


app = Flask(__name__)

# Load the CSV dataset
df = pd.read_csv("allergy_detection_data.csv")

# Load the trained model and label encoders
model = joblib.load('allergy_model.pkl')
main_symptom_encoder = joblib.load('Main Symptom_encoder.pkl')
affected_area_encoder = joblib.load('Affected Areas_encoder.pkl')
sub_allergy_type_encoder = joblib.load('Sub-Allergy Type_encoder.pkl')

# Image processing functions to extract grayscale and redness values
def calculate_grayscale_value(image_path):
    # Read the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return np.mean(image)

def calculate_redness_value(image_path):
    # Read the image in color (BGR format)
    image = cv2.imread(image_path)
    # Extract the red channel
    red_channel = image[:, :, 2]
    return np.mean(red_channel)

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/scan")
def scan():
    # Extract relevant columns from the dataset
    symptoms = df["Main Symptom"].unique()
    affected_areas = df["Affected Areas"].unique() 
    sub_allergy_types = df["Sub-Allergy Type"].unique() 
    return render_template("scan.html", symptoms=symptoms, affected_areas=affected_areas, sub_allergy_types=sub_allergy_types)

@app.route('/predict', methods=['POST'])
def predict_allergy():
    # Get the uploaded image and questionnaire data
    img = request.files['image']
    main_symptom = request.form['mainSymptom']
    affected_area = request.form['affectedArea']
    sub_allergy_type = request.form['subAllergyType']
    
    # Save the image to a temporary file
    img_path = os.path.join('static/uploads', img.filename)
    img.save(img_path)
    
    # Calculate grayscale and redness values
    grayscale_value = calculate_grayscale_value(img_path)
    redness_value = calculate_redness_value(img_path)
    
    # Define recommended medicines mapping for each allergy item
    allergy_medicine_mapping = {
        "Peanuts": ["Cetirizine", "Loratadine"],
        "Milk": ["Diphenhydramine", "Fexofenadine"],
        "Bee": ["Epinephrine (EpiPen)", "Antihistamines"],
        "Wheat": ["Cetirizine", "Prednisone"],
        "Dust Mites": ["Fluticasone", "Montelukast"],
        "Wasps": ["Epinephrine", "Hydrocortisone"],
        "Ants": ["Hydrocortisone", "Antihistamines"],
        "Oak": ["Loratadine", "Topical Steroids"],
        "Pine": ["Cetirizine", "Fexofenadine"],
        "Birch": ["Loratadine", "Nasal Sprays"],
        "Elm": ["Cetirizine", "Montelukast"],
        "Maple": ["Loratadine", "Cetirizine"],
    }
    
    # Check the dataset for a matching row
    matching_row = df[
        (df['Grayscale Value'] == grayscale_value) &
        (df['Redness Value'] == redness_value) &
        (df['Main Symptom'] == main_symptom) &
        (df['Affected Areas'] == affected_area) &
        (df['Sub-Allergy Type'] == sub_allergy_type)
    ]
    
    # If a matching row is found in the dataset
    if not matching_row.empty:
        allergy_type = matching_row.iloc[0]['Allergy Type']
        allergy_item = matching_row.iloc[0]['Allergy Item']
    else:
        # Preprocess questionnaire inputs
        main_symptom_encoded = main_symptom_encoder.transform([main_symptom])[0]
        affected_area_encoded = affected_area_encoder.transform([affected_area])[0]
        sub_allergy_type_encoded = sub_allergy_type_encoder.transform([sub_allergy_type])[0]
        
        # Combine all features
        features = np.array([[grayscale_value, redness_value, main_symptom_encoded, affected_area_encoded, sub_allergy_type_encoded]])
        
        # Predict the allergy type and item using the ML model
        prediction = model.predict(features)
        allergy_type, allergy_item = prediction[0]
    
    # Get recommended medicines for the detected allergy item
    recommended_medicines = allergy_medicine_mapping.get(allergy_item, ["No specific recommendation available."])

    # Pass the results to the template
    result = {
        'allergy_type': allergy_type,
        'allergy_item': allergy_item,
        'medicines': recommended_medicines
    }
    return render_template(
        'scan.html',
        symptoms=df["Main Symptom"].unique(),
        affected_areas=df["Affected Areas"].unique(),
        sub_allergy_types=df["Sub-Allergy Type"].unique(),
        result=result,
        uploaded_image_url=img_path,
        main_symptom=main_symptom,
        affected_area=affected_area,
        sub_allergy_type=sub_allergy_type
    )


if __name__ == '__main__':
    
    app.run(debug=True)