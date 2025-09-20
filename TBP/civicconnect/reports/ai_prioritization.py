import numpy as np
import pandas as pd
from django.utils.timezone import now
from reports.models import Issue
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ✅ Define priority mappings
PRIORITY_MAPPING = {"High": 3, "Medium": 2, "Low": 1}
HIGH_PRIORITY_ISSUES = {"accident", "fire", "emergency", "water leakage", "tree fallen", "gas leak", "bridge collapse"}
MEDIUM_PRIORITY_ISSUES = {"pothole", "flood", "broken road", "open manhole", "streetlight failure"}
LOW_PRIORITY_ISSUES = {"garbage", "noise", "graffiti", "stray animals", "general complaints"}

def compute_severity(description):
    """Assigns a severity score (1-5) based on issue keywords."""
    if not description:
        return 2  # Default moderate severity

    description = description.lower()
    words = set(description.split())  # Convert description into a set of words

    if words & HIGH_PRIORITY_ISSUES:
        return 4  # High severity
    elif words & MEDIUM_PRIORITY_ISSUES:
        return 3  # Medium severity
    elif words & LOW_PRIORITY_ISSUES:
        return 1  # Low severity
    return 2  # Default severity

def calculate_priority():
    """Dynamically updates issue priority based on frequency and severity."""
    issues = Issue.objects.all()
    if not issues.exists():
        print("⚠ No issues found.")
        return

    # Convert queryset to DataFrame
    data = pd.DataFrame(list(issues.values("id", "description", "report_count", "created_at")))

    if data.empty:
        print("⚠ No valid data to process.")
        return

    # ✅ Compute severity based on description
    data["severity"] = data["description"].apply(compute_severity)

    # ✅ Normalize report count using log function
    data["normalized_reports"] = np.log1p(data["report_count"])

    # ✅ Compute priority score with restricted report impact on low severity
    def compute_priority_score(row):
        if row["severity"] == 1:
            return 1.0  # Fixed for low severity
        else:
            return (0.7 * row["severity"]) + (0.3 * row["normalized_reports"])

    data["priority_score"] = data.apply(compute_priority_score, axis=1)

    # ✅ Assign priority levels based on computed score
    def assign_priority(score):
        if score > 4:
            return 3  # High
        elif score > 2.5:
            return 2  # Medium
        return 1  # Low

    data["priority"] = data["priority_score"].apply(assign_priority)

    # ✅ Bulk update database records
    updates = [
        Issue(id=row["id"], severity=row["severity"], priority_score=row["priority_score"], priority=row["priority"])
        for _, row in data.iterrows()
    ]

    Issue.objects.bulk_update(updates, ["severity", "priority_score", "priority"])
    print(f"✅ Prioritization Completed! Updated {len(updates)} issues.")

def is_similar_issue(new_desc, existing_desc_list, threshold=0.8):
    """Checks if the new issue description is similar to any existing ones using TF-IDF."""
    if not existing_desc_list or not new_desc:
        return False, None

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([new_desc] + existing_desc_list)

    # Compute cosine similarity
    similarity_scores = cosine_similarity(vectors[0], vectors[1:])[0]

    # Find highest similarity score
    if similarity_scores.size > 0:
        max_score = np.max(similarity_scores)
        max_index = np.argmax(similarity_scores)

        if max_score >= threshold:
            return True, max_index  # Return True and index of most similar issue
    return False, None
