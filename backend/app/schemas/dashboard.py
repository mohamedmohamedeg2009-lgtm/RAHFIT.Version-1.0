from app.models.dashboard import DashboardSummaryView, DashboardView


class DashboardResponse(DashboardView):
    """Stable API response contract for the authenticated dashboard aggregate."""


class DashboardSummaryResponse(DashboardSummaryView):
    """Stable response for the record-backed dashboard summary endpoint."""
