from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Report, Category
from .forms import ReportForm


REPORTS_PER_PAGE = 10


class OwnerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only the owner of a report can access it."""

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You can only edit your own reports.")
        return redirect("reports:detail", pk=self.get_object().pk)


class LostReportCreateView(LoginRequiredMixin, CreateView):
    """Create a lost item report."""
    model = Report
    form_class = ReportForm
    template_name = "reports/report_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.report_type = Report.ReportType.LOST
        response = super().form_valid(form)
        messages.success(self.request, "Lost item report created successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Report a Lost Item"
        context["report_type"] = "Lost"
        return context

    def get_success_url(self):
        return reverse_lazy("reports:detail", kwargs={"pk": self.object.pk})


class FoundReportCreateView(LoginRequiredMixin, CreateView):
    """Create a found item report."""
    model = Report
    form_class = ReportForm
    template_name = "reports/report_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.report_type = Report.ReportType.FOUND
        response = super().form_valid(form)
        messages.success(self.request, "Found item report created successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Report a Found Item"
        context["report_type"] = "Found"
        return context

    def get_success_url(self):
        return reverse_lazy("reports:detail", kwargs={"pk": self.object.pk})


class ReportDetailView(DetailView):
    """View a report's details."""
    model = Report
    template_name = "reports/report_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_owner"] = self.object.user == self.request.user
        return context


class ReportUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Edit own report."""
    model = Report
    form_class = ReportForm
    template_name = "reports/report_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Report updated successfully!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Report"
        context["is_edit"] = True
        return context

    def get_success_url(self):
        return reverse_lazy("reports:detail", kwargs={"pk": self.object.pk})


class ReportDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Delete own report."""
    model = Report
    template_name = "reports/report_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("reports:my_reports")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Report deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def mark_recovered_view(request, pk):
    """Mark a report as recovered (owner-only, POST only)."""
    report = get_object_or_404(Report, pk=pk)

    if report.user != request.user:
        messages.error(request, "You can only recover your own reports.")
        return redirect("reports:detail", pk=report.pk)

    if request.method == "POST":
        report.mark_recovered()
        messages.success(request, "Report marked as recovered!")

    return redirect("reports:detail", pk=report.pk)


def report_list(request):
    qs = Report.objects.select_related("category", "user").order_by("-created_at")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(location__icontains=q)
        )

    report_type = request.GET.get("type", "")
    valid_types = {choice[0] for choice in getattr(Report.ReportType, "choices", ())}
    if report_type in valid_types:
        qs = qs.filter(report_type=report_type)

    category_id = request.GET.get("category", "")
    if category_id.isdigit():
        qs = qs.filter(category_id=int(category_id))

    status = request.GET.get("status", "")
    if status == "open":
        qs = qs.filter(status=Report.Status.OPEN)
    elif status == "recovered":
        qs = qs.filter(status=Report.Status.RECOVERED)

    paginator = Paginator(qs, REPORTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "reports": page_obj.object_list,
        "categories": Category.objects.order_by("name"),
        "q": q,
        "selected_type": report_type,
        "selected_category": category_id,
        "selected_status": status,
    }
    return render(request, "reports/report_list.html", context)


def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related("category", "user"),
        pk=pk,
    )
    return render(
        request,
        "reports/report_detail.html",
        {
            "report": report,
            "is_owner": request.user.is_authenticated and report.user == request.user,
        },
    )


@login_required
def my_reports(request):
    qs = Report.objects.filter(user=request.user).select_related("category").order_by("-created_at")

    status = request.GET.get("status", "")
    if status == "open":
        qs = qs.filter(status=Report.Status.OPEN)
    elif status == "recovered":
        qs = qs.filter(status=Report.Status.RECOVERED)

    paginator = Paginator(qs, REPORTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    user_reports = Report.objects.filter(user=request.user)

    context = {
        "page_obj": page_obj,
        "reports": page_obj.object_list,
        "selected_status": status,
        "total": user_reports.count(),
        "open_count": user_reports.filter(status=Report.Status.OPEN).count(),
        "recovered_count": user_reports.filter(status=Report.Status.RECOVERED).count(),
    }
    return render(request, "reports/my_reports.html", context)


def stats(request):
    context = {
        "total_reports": Report.objects.count(),
        "lost_count": Report.objects.filter(report_type=Report.ReportType.LOST).count(),
        "found_count": Report.objects.filter(report_type=Report.ReportType.FOUND).count(),
        "recovered_count": Report.objects.filter(status=Report.Status.RECOVERED).count(),
        "by_category": Category.objects.annotate(report_count=Count("reports")).order_by("-report_count"),
        "recent": Report.objects.select_related("category", "user").order_by("-created_at")[:5],
    }
    return render(request, "reports/stats.html", context)
