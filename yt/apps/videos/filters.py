from datetime import timedelta

import django_filters
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from .models import Video

UPLOAD_DATE_STATUSES = (
    ('last_hour', 'Last hour'),
    ('today', 'Today'),
    ('this_week', 'This week'),
    ('this_month', 'This month'),
    ('this_year', 'This year'),
)


class VideoFilter(django_filters.FilterSet):
    uploaded = django_filters.ChoiceFilter(choices=UPLOAD_DATE_STATUSES, method='get_uploaded')

    class Meta:
        model = Video
        fields = ['uploaded']

    def get_uploaded(self, queryset, name, value):
        timedelta_statuses = {
            'last_hour': timedelta(hours=1),
            'today': timedelta(days=1),
            'this_week': timedelta(days=7),
            'this_month': relativedelta(months=1),
            'this_year': relativedelta(years=1),
        }
        filter_status = timedelta_statuses.get(value)

        if value and filter_status:
            return queryset.filter(created_at__gt=timezone.now() - filter_status)

        return queryset
