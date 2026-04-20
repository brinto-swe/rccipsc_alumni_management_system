"""Directory filters."""

import django_filters

from profiles.models import AlumniProfile


class AlumniDirectoryFilterSet(django_filters.FilterSet):
    profession = django_filters.CharFilter(method="filter_profession")

    class Meta:
        model = AlumniProfile
        fields = ["batch_year", "academic_group", "current_city", "current_country"]

    def filter_profession(self, queryset, name, value):
        return queryset.filter(
            professions__present_occupation__icontains=value
        ) | queryset.filter(
            professions__role__icontains=value
        ) | queryset.filter(
            professions__institution_or_organization_name__icontains=value
        )
