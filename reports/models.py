from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Categories for lost and found items (e.g., Electronics, Keys, Books)."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Report(models.Model):
    """Unified model for both lost and found item reports."""
    
    class ReportType(models.TextChoices):
        LOST = "LOST", "Lost"
        FOUND = "FOUND", "Found"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        RECOVERED = "RECOVERED", "Recovered"

    # Core fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    
    # Classification
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports"
    )
    report_type = models.CharField(
        max_length=10,
        choices=ReportType.choices
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN
    )
    
    # Location and timing
    location = models.CharField(max_length=150)
    event_date = models.DateField()  # date lost or found
    
    # Media and contact
    image = models.ImageField(upload_to="reports/", blank=True, null=True)
    contact_info = models.CharField(max_length=150, blank=True)
    
    # Status tracking
    recovered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type", "status"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["event_date"]),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"
    
    def mark_recovered(self):
        """Mark this report as recovered."""
        self.status = self.Status.RECOVERED
        self.recovered_at = timezone.now()
        self.save()
