import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import warnings
warnings.filterwarnings('ignore')

import pickle

# 🔹 Load trained model
with open("ai_severity_model.pkl", "rb") as f:
    model = pickle.load(f)

# 🔹 Load TF-IDF vectorizer (instead of SentenceTransformer)
with open("tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# 🔹 Test civic issue descriptions
test_descriptions = [
    "There is a huge pothole on the main road, causing accidents.",   # High
    "Streetlight is flickering, making it difficult to see at night.",  # Medium
    "A garbage bin is overflowing near the park entrance.",  # Low
]

# 🔹 Transform using the TF-IDF vectorizer
X_test = vectorizer.transform(test_descriptions)

# 🔹 Predict severity
y_pred = model.predict(X_test)

# 🔹 Map output back to severity labels
severity_map = {0: "Low", 1: "Medium", 2: "High"}
predicted_labels = [severity_map[label] for label in y_pred]

# 🔹 Output predictions
for desc, label in zip(test_descriptions, predicted_labels):
    print(f"📝 '{desc}' ➡️ Predicted Severity: {label}")
