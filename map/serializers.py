from rest_framework import serializers

from map.models import CommunityArea, RestaurantPermit


class CommunityAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityArea
        fields = ["name", "num_permits"]

    num_permits = serializers.SerializerMethodField()

    def get_num_permits(self, obj):
        request = self.context.get("request")
        year = request.query_params.get("year") if request else None

        permits = RestaurantPermit.objects.filter(
            community_area_id=str(obj.area_id)
        )

        if year:
            permits = permits.filter(issue_date__year=year)

        return permits.count()

