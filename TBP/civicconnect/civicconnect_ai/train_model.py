import pandas as pd
import pickle
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
import xgboost as xgb

# 📥 Load dataset
df = pd.read_csv("issues_dataset.csv", encoding="utf-8", on_bad_lines="skip")
df.dropna(subset=["description", "severity"], inplace=True)

# 🔢 Convert severity to numeric
df["severity"] = pd.to_numeric(df["severity"], errors="coerce")
df.dropna(subset=["severity"], inplace=True)

# 🧽 Normalize severity values to 3 classes
severity_mapping = {2: 0, 3: 1, 4: 2}
df["severity"] = df["severity"].map(severity_mapping)
df.dropna(subset=["severity"], inplace=True)
df["severity"] = df["severity"].astype(int)

# ➕ Manual oversampling of minority classes (min 5 per class)
df_minority_1 = df[df["severity"] == 1]
df_minority_2 = df[df["severity"] == 2]

df_minority_1_upsampled = df_minority_1.sample(n=max(5, len(df_minority_1)), replace=True, random_state=42)
df_minority_2_upsampled = df_minority_2.sample(n=max(5, len(df_minority_2)), replace=True, random_state=42)

df = pd.concat([df, df_minority_1_upsampled, df_minority_2_upsampled])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ✍️ TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X = vectorizer.fit_transform(df["description"])
y = df["severity"]

# 💾 Save vectorizer
with open("civicconnect_ai/tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

# 📊 Class distribution before SMOTE
class_counts = Counter(y)
print(f"Class distribution before SMOTE: {class_counts}")

# ✅ Apply SMOTE if all classes > 4 samples
if all(count > 4 for count in class_counts.values()):
    smote = SMOTE(sampling_strategy="auto", k_neighbors=2, random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    print("✅ SMOTE applied successfully!")
else:
    X_resampled, y_resampled = X, y
    print("⚠️ SMOTE skipped: Not enough samples in one or more classes.")

# ⚖️ Compute class weights
class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.array([0, 1, 2]),
    y=y_resampled
)
class_weight_dict = {i: float(w) for i, w in enumerate(class_weights)}
print("Computed class weights:", class_weight_dict)

# ✂️ Stratified train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled,
    y_resampled,
    test_size=0.3,
    stratify=y_resampled,
    random_state=42
)

# 🚀 Train XGBoost model
model = xgb.XGBClassifier(
    objective="multi:softmax",
    num_class=3,
    eval_metric="mlogloss",
    n_estimators=150,
    learning_rate=0.03,
    max_depth=6,
    min_child_weight=2,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_lambda=15,
    random_state=42,
    scale_pos_weight=class_weight_dict  # Apply class weights to handle imbalance
)

model.fit(X_train, y_train)

# 💾 Save trained model
with open("civicconnect_ai/ai_severity_model.pkl", "wb") as f:
    pickle.dump(model, f)

# 📈 Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n📊 Model Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
