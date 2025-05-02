from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import xgboost as xgb
import warnings

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

warnings.filterwarnings("ignore", category=UserWarning)


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use MySQL or PostgreSQL URI for other DBs
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)   

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create the DB and tables (only the first time)
with app.app_context():
    db.create_all()



# Load the model and preprocessor
with open('best_xgb_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)
with open('preprocessor.pkl', 'rb') as preprocessor_file:
    preprocessor = pickle.load(preprocessor_file)

# xgb_model = xgb.XGBClassifier()
# # Define all columns (categorical and numerical)
# all_cols = ['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure', 
#             'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity', 
#             'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 
#             'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod', 
#             'MonthlyCharges', 'TotalCharges']

@app.route('/')
def Home():
    return render_template('Home.html')

@app.route('/index')
def index():
    return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     input_data = request.form.to_dict()
#     input_df = pd.DataFrame([input_data])
    
#     # Ensure all expected columns are present in the input DataFrame
#     for col in all_cols:
#         if col not in input_df.columns:
#             input_df[col] = 0  # Or any default value suitable for the column

#     # Reorder columns to match the training data order
#     input_df = input_df[all_cols] 

#     # Convert numeric columns to proper types
#     numeric_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
#     input_df[numeric_cols] = input_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

#     # Handle missing or invalid values 
#     input_df.fillna(0, inplace=True)  

#     # Encode categorical columns and print encoded values
#     categorical_cols = [col for col in all_cols if col not in numeric_cols]
#     for col in categorical_cols:
#         # Replace unseen values with the most frequent category
#         valid_classes = encoders[col].classes_
#         input_df[col] = input_df[col].apply(lambda x: x if str(x) in valid_classes else valid_classes[0])
#         # Transform using the encoder
#         input_df[col] = encoders[col].transform(input_df[col].astype(str))
#         print(f"Encoded values for {col}: {input_df[col].values}")  # Print encoded values

#     # Make prediction (no need to convert to DMatrix)
#     prediction = model.predict(input_df)[0]
#     prediction_text = "Churn" if prediction == 1 else "Not Churn"  
#     print(f"Prediction: {prediction_text}")

#     # return render_template('results.html', prediction_text=prediction_text)
#     return render_template('index.html', prediction_text=prediction_text)


# Get the feature names used during training (from the preprocessor)
categorical_features = preprocessor.transformers_[1][2]
# Accessing one-hot encoder to get categories
onehot_encoder = preprocessor.transformers_[1][1]['onehot']


# Get the feature names used during training (from the preprocessor)
categorical_features = preprocessor.transformers_[1][2]
# Accessing one-hot encoder to get categories
onehot_encoder = preprocessor.transformers_[1][1]['onehot']


feature_names = ['gender',
 'SeniorCitizen',
 'Partner',
 'Dependents',
 'tenure',
 'PhoneService',
 'MultipleLines',
 'InternetService',
 'OnlineSecurity',
 'OnlineBackup',
 'DeviceProtection',
 'TechSupport',
 'StreamingTV',
 'StreamingMovies',
 'Contract',
 'PaperlessBilling',
 'PaymentMethod',
 'MonthlyCharges',
 'TotalCharges']
for i, category in enumerate(onehot_encoder.categories_):
    feature_names.extend([f"{categorical_features[i]}_{value}" for value in category[1:]])


numeric_cols = preprocessor.transformers_[0][2]
all_cols = numeric_cols + feature_names
@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.form.to_dict()
    input_df = pd.DataFrame([input_data])

    # Ensure numeric conversion
    numeric_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    for col in numeric_cols:
        input_df[col] = pd.to_numeric(input_df.get(col, 0), errors='coerce')

    input_df.fillna(0, inplace=True)

   

    # Reorder and align input_df to match training features
    # This is automatic if preprocessor was trained on the full X DataFrame
    processed_data = preprocessor.transform(input_df)

    prediction = model.predict(processed_data)[0]
    prediction_text = "Churn" if prediction == 1 else "Not Churn"

    return render_template('index.html', prediction_text=prediction_text)


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message="User already exists")

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(success=True, message="User registered successfully")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return jsonify(success=True, message="Login successful", redirect="/index")
    return jsonify(success=False, message="Invalid credentials")

if __name__ == '__main__':
    app.run(debug=True) 