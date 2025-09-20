from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F, Q
import math
from sentence_transformers import util
import pickle
import os

User = get_user_model()

_model = None  # Cache for SentenceTransformer
_ml_model = None  # Cache for ML severity model
_vectorizer = None  # Cache for TF-IDF vectorizer


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def get_severity_model():
    global _ml_model, _vectorizer
    if _ml_model is None or _vectorizer is None:
        base_path = os.path.join(os.path.dirname(__file__), '../civicconnect_ai')
        with open(os.path.join(base_path, "ai_severity_model.pkl"), "rb") as f:
            _ml_model = pickle.load(f)
        with open(os.path.join(base_path, "tfidf_vectorizer.pkl"), "rb") as f:
            _vectorizer = pickle.load(f)
    return _ml_model, _vectorizer


def compute_severity(description, is_urgent=False):
    emergency_keywords = [
        "fire", "flood", "gas leak", "earthquake", "emergency", "explosion",
        "collapsed", "accident", "hazard", "toxic", "fatal", "ambulance"
    ]

    lowered = description.lower()

    if is_urgent or any(word in lowered for word in emergency_keywords):
        print(f"Emergency detected in description: {description}")
        return 3  # High severity for emergencies

    model, vectorizer = get_severity_model()
    X = vectorizer.transform([description])
    prediction = model.predict(X)[0]

    print(f"Severity predicted by model: {prediction}")

    severity_map = {0: 1, 1: 2, 2: 3}
    return severity_map.get(prediction, 1)


class Officer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class Issue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    title = models.CharField(max_length=255, default="Untitled Issue", blank=True)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Solved', 'Solved')],
        default='Pending'
    )
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to="issue_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    report_count = models.IntegerField(default=1)
    severity = models.IntegerField(default=1)
    priority_score = models.FloatField(default=0.0)
    priority = models.IntegerField(default=0)

    assigned_officer = models.ForeignKey('Officer', on_delete=models.SET_NULL, null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)
    work_images = models.ImageField(upload_to='work_images/', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['description', 'latitude', 'longitude'], name='unique_issue_location')
        ]

    def __str__(self):
        return f"Issue by {self.username} at {self.location_name} (Severity: {self.severity}, Priority: {self.priority})"

    def save(self, *args, **kwargs):
        if not self.assigned_officer and self.priority == 3:
            officer = Officer.objects.order_by("?").first()
            if officer:
                self.assigned_officer = officer
        super().save(*args, **kwargs)

    def update_priority(self):
        # Check if the issue is urgent (contains emergency keywords)
        self.severity = compute_severity(self.description, is_urgent=True)

        # Calculate priority score
        score = (self.severity * 1.5) + math.log(self.report_count + 1)
        self.priority_score = round(score, 2)

        # Decide priority level
        if self.severity == 3:
            self.priority = 3
        elif score >= 4:
            self.priority = 2
        else:
            self.priority = 1

        # Assign officer if needed
        if self.priority == 3 and not self.assigned_officer:
            self.assigned_officer = Officer.objects.order_by("?").first()

        self.save(update_fields=["severity", "priority_score", "priority", "assigned_officer"])

    def compute_description_similarity(self, other_description):
        model = get_model()
        emb_self = model.encode(self.description, convert_to_tensor=True)
        emb_other = model.encode(other_description, convert_to_tensor=True)
        return util.pytorch_cos_sim(emb_self, emb_other).item()

    def report_issue(self, user):
        if ReportedUser.objects.filter(issue=self, user=user).exists():
            return False

        similar_issues = Issue.objects.filter(
            Q(location_name__icontains=self.location_name) |
            (
                Q(latitude__range=(self.latitude - 0.001, self.latitude + 0.001)) &
                Q(longitude__range=(self.longitude - 0.001, self.longitude + 0.001))
            )
        )

        model = get_model()
        emb_self = model.encode(self.description, convert_to_tensor=True)

        for issue in similar_issues:
            emb_existing = model.encode(issue.description, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(emb_self, emb_existing).item()
            if similarity > 0.75:
                issue.report_count = F('report_count') + 1
                issue.save(update_fields=["report_count"])
                issue.refresh_from_db()
                ReportedUser.objects.create(issue=issue, user=user)
                issue.update_priority()
                return True

        self.report_count = 1
        self.save()
        ReportedUser.objects.create(issue=self, user=user)
        self.update_priority()
        return True


class ReportedUser(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='reported_user_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('issue', 'user')

    def __str__(self):
        return f"{self.user.username} reported {self.issue.location_name}"
