from datetime import date

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .models import Category, Report



class CategoryModelTests(TestCase):
    """Test Category model."""
    
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
    
    def test_category_creation(self):
        """Test that a category can be created."""
        self.assertTrue(Category.objects.exists())
        self.assertEqual(str(self.category), "Electronics")
    
    def test_category_unique_name(self):
        """Test that category names must be unique."""
        with self.assertRaises(Exception):
            Category.objects.create(name="Electronics")


class ReportModelTests(TestCase):
    """Test Report model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Electronics")
        self.report = Report.objects.create(
            user=self.user,
            title="Lost iPhone",
            description="Black iPhone 15",
            category=self.category,
            report_type=Report.ReportType.LOST,
            location="Library",
            event_date=date.today()
        )
    
    def test_report_creation(self):
        """Test that a report can be created."""
        self.assertTrue(Report.objects.exists())
        self.assertEqual(self.report.user, self.user)
        self.assertEqual(self.report.status, Report.Status.OPEN)
    
    def test_report_string_representation(self):
        """Test report's string representation."""
        expected = "Lost - Lost iPhone"
        self.assertEqual(str(self.report), expected)
    
    def test_mark_recovered(self):
        """Test marking a report as recovered."""
        self.assertEqual(self.report.status, Report.Status.OPEN)
        self.assertIsNone(self.report.recovered_at)
        
        self.report.mark_recovered()
        
        self.assertEqual(self.report.status, Report.Status.RECOVERED)
        self.assertIsNotNone(self.report.recovered_at)
    
    def test_report_has_timestamps(self):
        """Test that reports have creation and update timestamps."""
        self.assertIsNotNone(self.report.created_at)
        self.assertIsNotNone(self.report.updated_at)
    
    def test_found_report_creation(self):
        """Test creating a found item report."""
        found_report = Report.objects.create(
            user=self.user,
            title="Found Keys",
            description="Silver keys with blue keychain",
            category=self.category,
            report_type=Report.ReportType.FOUND,
            location="Student Center",
            event_date=date.today()
        )
        self.assertEqual(found_report.report_type, Report.ReportType.FOUND)


class LostReportCreateViewTests(TestCase):
    """Test LostReportCreateView."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Electronics")
        self.url = reverse("reports:lost_create")
    
    def test_anonymous_user_cannot_create_report(self):
        """Test that anonymous users are redirected to login."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
    
    def test_authenticated_user_can_access_form(self):
        """Test that logged-in users can access the create form."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
    
    def test_create_lost_report_success(self):
        """Test creating a lost report successfully."""
        self.client.login(username="testuser", password="testpass123")
        
        data = {
            "title": "Lost Wallet",
            "description": "Brown leather wallet",
            "category": self.category.id,
            "location": "Near Gate 1",
            "event_date": date.today(),
            "contact_info": "0123456789"
        }
        response = self.client.post(self.url, data)
        
        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        
        # Report should be created with correct type
        report = Report.objects.first()
        self.assertEqual(report.title, "Lost Wallet")
        self.assertEqual(report.report_type, Report.ReportType.LOST)
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.status, Report.Status.OPEN)


class FoundReportCreateViewTests(TestCase):
    """Test FoundReportCreateView."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Books")
        self.url = reverse("reports:found_create")
    
    def test_create_found_report_success(self):
        """Test creating a found report successfully."""
        self.client.login(username="testuser", password="testpass123")
        
        data = {
            "title": "Found Notebook",
            "description": "Blue notebook with name inside",
            "category": self.category.id,
            "location": "Library Second Floor",
            "event_date": date.today(),
            "contact_info": "0987654321"
        }
        response = self.client.post(self.url, data)
        
        report = Report.objects.first()
        self.assertEqual(report.report_type, Report.ReportType.FOUND)


class ReportDetailViewTests(TestCase):
    """Test ReportDetailView."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Electronics")
        self.report = Report.objects.create(
            user=self.user,
            title="Lost Phone",
            description="Test phone",
            category=self.category,
            report_type=Report.ReportType.LOST,
            location="Campus",
            event_date=date.today()
        )
        self.url = reverse("reports:detail", kwargs={"pk": self.report.pk})
    
    def test_detail_page_is_public(self):
        """Test that detail pages are accessible to anonymous users."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["report"], self.report)
    
    def test_owner_flag_is_true_for_owner(self):
        """Test that is_owner is True for the report owner."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_owner"])
    
    def test_owner_flag_is_false_for_non_owner(self):
        """Test that is_owner is False for non-owners."""
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.get(self.url)
        self.assertFalse(response.context["is_owner"])


class ReportUpdateViewTests(TestCase):
    """Test ReportUpdateView (owner-only edit)."""
    
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username="owner",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Electronics")
        self.report = Report.objects.create(
            user=self.owner,
            title="Lost Watch",
            description="Black watch",
            category=self.category,
            report_type=Report.ReportType.LOST,
            location="Campus",
            event_date=date.today()
        )
        self.url = reverse("reports:edit", kwargs={"pk": self.report.pk})
    
    def test_non_owner_cannot_edit(self):
        """Test that non-owners cannot edit reports."""
        self.client.login(username="other", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_owner_can_edit(self):
        """Test that owners can edit their reports."""
        self.client.login(username="owner", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_edit_report_updates_data(self):
        """Test that editing a report updates its data."""
        self.client.login(username="owner", password="testpass123")
        
        data = {
            "title": "Lost Watch - Updated",
            "description": "Black watch - more details",
            "category": self.category.id,
            "location": "Campus Near Gate",
            "event_date": date.today(),
            "contact_info": "9876543210"
        }
        response = self.client.post(self.url, data)
        
        self.report.refresh_from_db()
        self.assertEqual(self.report.title, "Lost Watch - Updated")
        self.assertEqual(self.report.contact_info, "9876543210")


class ReportDeleteViewTests(TestCase):
    """Test ReportDeleteView (owner-only delete)."""
    
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username="owner",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Electronics")
        self.report = Report.objects.create(
            user=self.owner,
            title="Lost Bag",
            description="Black bag",
            category=self.category,
            report_type=Report.ReportType.LOST,
            location="Campus",
            event_date=date.today()
        )
        self.url = reverse("reports:delete", kwargs={"pk": self.report.pk})
    
    def test_non_owner_cannot_delete(self):
        """Test that non-owners cannot delete reports."""
        self.client.login(username="other", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_owner_can_delete(self):
        """Test that owners can delete their reports."""
        self.client.login(username="owner", password="testpass123")
        report_id = self.report.pk
        
        response = self.client.post(self.url)
        
        self.assertFalse(Report.objects.filter(pk=report_id).exists())


class MarkRecoveredViewTests(TestCase):
    """Test mark_recovered_view function."""
    
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username="owner",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Electronics")
        self.report = Report.objects.create(
            user=self.owner,
            title="Lost Item",
            description="Test item",
            category=self.category,
            report_type=Report.ReportType.LOST,
            location="Campus",
            event_date=date.today()
        )
        self.url = reverse("reports:recover", kwargs={"pk": self.report.pk})
    
    def test_non_owner_cannot_mark_recovered(self):
        """Test that non-owners cannot mark reports as recovered."""
        self.client.login(username="other", password="testpass123")
        response = self.client.post(self.url)
        
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.OPEN)
    
    def test_owner_can_mark_recovered(self):
        """Test that owners can mark their reports as recovered."""
        self.client.login(username="owner", password="testpass123")
        response = self.client.post(self.url)
        
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.RECOVERED)
        self.assertIsNotNone(self.report.recovered_at)
    
    def test_mark_recovered_sets_timestamp(self):
        """Test that marking recovered sets the timestamp."""
        self.client.login(username="owner", password="testpass123")
        self.assertIsNone(self.report.recovered_at)
        
        self.client.post(self.url)
        
        self.report.refresh_from_db()
        self.assertIsNotNone(self.report.recovered_at)

def make_user(username="testuser", password="pass1234"):
    return User.objects.create_user(username=username, password=password)


def make_report(
    user,
    title="Lost Keys",
    report_type=Report.ReportType.LOST,
    status=Report.Status.OPEN,
    category=None,
):
    return Report.objects.create(
        user=user,
        title=title,
        description="Found near the library.",
        location="Main Library",
        event_date=date.today(),
        report_type=report_type,
        status=status,
        category=category,
    )


class CategoryBootstrapTests(TestCase):
    def test_report_list_seeds_categories_when_empty(self):
        self.assertEqual(Category.objects.count(), 0)

        response = self.client.get(reverse("reports:report_list"))

        self.assertEqual(response.status_code, 200)
        self.assertGreater(Category.objects.count(), 0)
        self.assertContains(response, "All Categories")


class PublicReportListViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.category = Category.objects.create(name="Electronics")
        self.report_one = make_report(
            self.user,
            title="Lost Phone",
            report_type=Report.ReportType.LOST,
            category=self.category,
        )
        self.report_two = make_report(
            self.user,
            title="Found Wallet",
            report_type=Report.ReportType.FOUND,
        )

    def test_list_accessible_anonymously(self):
        response = self.client.get(reverse("reports:report_list"))
        self.assertEqual(response.status_code, 200)

    def test_list_shows_all_reports(self):
        response = self.client.get(reverse("reports:report_list"))
        self.assertContains(response, "Lost Phone")
        self.assertContains(response, "Found Wallet")

    def test_search_by_title(self):
        response = self.client.get(reverse("reports:report_list"), {"q": "Phone"})
        self.assertContains(response, "Lost Phone")
        self.assertNotContains(response, "Found Wallet")

    def test_search_by_location(self):
        response = self.client.get(reverse("reports:report_list"), {"q": "library"})
        self.assertContains(response, "Lost Phone")

    def test_filter_by_type_lost(self):
        response = self.client.get(reverse("reports:report_list"), {"type": Report.ReportType.LOST})
        self.assertContains(response, "Lost Phone")
        self.assertNotContains(response, "Found Wallet")

    def test_filter_by_type_found(self):
        response = self.client.get(reverse("reports:report_list"), {"type": Report.ReportType.FOUND})
        self.assertContains(response, "Found Wallet")
        self.assertNotContains(response, "Lost Phone")

    def test_filter_by_category(self):
        response = self.client.get(reverse("reports:report_list"), {"category": self.category.pk})
        self.assertContains(response, "Lost Phone")
        self.assertNotContains(response, "Found Wallet")

    def test_filter_by_status_open(self):
        make_report(self.user, title="Recovered Bag", status=Report.Status.RECOVERED)
        response = self.client.get(reverse("reports:report_list"), {"status": "open"})
        self.assertContains(response, "Lost Phone")
        self.assertNotContains(response, "Recovered Bag")

    def test_filter_by_status_recovered(self):
        make_report(self.user, title="Recovered Bag", status=Report.Status.RECOVERED)
        response = self.client.get(reverse("reports:report_list"), {"status": "recovered"})
        self.assertContains(response, "Recovered Bag")
        self.assertNotContains(response, "Lost Phone")

    def test_pagination(self):
        for i in range(15):
            make_report(self.user, title=f"Item {i}")
        response = self.client.get(reverse("reports:report_list"), {"page": 1})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["page_obj"].has_next())


class MyReportsViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.other = make_user("other", "pass1234")
        self.my_report = make_report(self.user, title="My Lost Keys")
        self.other_report = make_report(self.other, title="Other Report")

    def test_my_reports_requires_login(self):
        url = reverse("reports:my_reports")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response.url)

    def test_my_reports_shows_only_own_reports(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reports:my_reports"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Lost Keys")
        self.assertNotContains(response, "Other Report")

    def test_my_reports_status_filter_open(self):
        make_report(self.user, title="Recovered Item", status=Report.Status.RECOVERED)
        self.client.force_login(self.user)
        response = self.client.get(reverse("reports:my_reports"), {"status": "open"})
        self.assertContains(response, "My Lost Keys")
        self.assertNotContains(response, "Recovered Item")

    def test_my_reports_status_filter_recovered(self):
        make_report(self.user, title="Recovered Item", status=Report.Status.RECOVERED)
        self.client.force_login(self.user)
        response = self.client.get(reverse("reports:my_reports"), {"status": "recovered"})
        self.assertContains(response, "Recovered Item")
        self.assertNotContains(response, "My Lost Keys")

    def test_my_reports_summary_counts(self):
        make_report(self.user, title="Recovered", status=Report.Status.RECOVERED)
        self.client.force_login(self.user)
        response = self.client.get(reverse("reports:my_reports"))
        self.assertEqual(response.context["total"], 2)
        self.assertEqual(response.context["open_count"], 1)
        self.assertEqual(response.context["recovered_count"], 1)


class StatsViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.category = Category.objects.create(name="Accessories")
        make_report(self.user, title="Lost A", report_type=Report.ReportType.LOST, category=self.category)
        make_report(self.user, title="Found B", report_type=Report.ReportType.FOUND, category=self.category)
        make_report(
            self.user,
            title="Recovered C",
            report_type=Report.ReportType.LOST,
            status=Report.Status.RECOVERED,
            category=self.category,
        )

    def test_stats_accessible_anonymously(self):
        response = self.client.get(reverse("reports:stats"))
        self.assertEqual(response.status_code, 200)

    def test_stats_counts(self):
        response = self.client.get(reverse("reports:stats"))
        self.assertEqual(response.context["total_reports"], 3)
        self.assertEqual(response.context["lost_count"], 2)
        self.assertEqual(response.context["found_count"], 1)
        self.assertEqual(response.context["recovered_count"], 1)
