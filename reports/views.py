from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView
)
from django.urls import reverse_lazy
from .models import Report, Category
from .forms import ReportForm


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
        # Fallback to reports list if my_reports is not available yet
        try:
            return reverse_lazy("my_reports")
        except:
            return reverse_lazy("reports:list")
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Report deleted successfully!")
        return super().delete(request, *args, **kwargs)


def mark_recovered_view(request, pk):
    """Mark a report as recovered (owner-only, POST only)."""
    report = get_object_or_404(Report, pk=pk)
    
    # Check ownership
    if report.user != request.user:
        messages.error(request, "You can only recover your own reports.")
        return redirect("reports:detail", pk=report.pk)
    
    # Only process POST requests
    if request.method == "POST":
        report.mark_recovered()
        messages.success(request, "Report marked as recovered!")
    
    return redirect("reports:detail", pk=report.pk)

