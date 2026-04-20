"""Serializers for profession APIs."""

from rest_framework import serializers

from professions.models import Profession


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = [
            "id",
            "profile",
            "present_occupation",
            "role",
            "institution_or_organization_name",
            "starting_date",
            "ending_date",
            "currently_working_here",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["profile", "created_at", "updated_at"]

    def validate(self, attrs):
        starting_date = attrs.get("starting_date", getattr(self.instance, "starting_date", None))
        ending_date = attrs.get("ending_date", getattr(self.instance, "ending_date", None))
        currently_working_here = attrs.get(
            "currently_working_here",
            getattr(self.instance, "currently_working_here", False),
        )
        if currently_working_here and ending_date:
            raise serializers.ValidationError(
                {"ending_date": "Leave ending date empty when currently working here is true."}
            )
        if not currently_working_here and not ending_date:
            raise serializers.ValidationError(
                {"ending_date": "Ending date is required when not currently working here."}
            )
        if starting_date and ending_date and ending_date < starting_date:
            raise serializers.ValidationError(
                {"ending_date": "Ending date cannot be earlier than the starting date."}
            )
        return attrs
