import pytest
from datetime import date

from django.shortcuts import reverse
from rest_framework.test import APIClient

from map.models import CommunityArea, RestaurantPermit

@pytest.fixture
def create_permit():
    def _create_permit(area, year, month, day):
        return RestaurantPermit.objects.create(
            community_area_id=str(area.area_id),
            issue_date=date(year, month, day),
        )
    return _create_permit

@pytest.mark.django_db
class TestMapDataView:
    def get_num_permits_by_name(self, response):
        data = response.json()
        return {item["name"]: item["num_permits"] for item in data}
    
    def get_area_data_by_name(self, response):
        data = response.json()
        return {item["name"]: item for item in data}
    
    def test_returns_permit_counts_for_selected_year(self, create_permit):
        # Arrange
        beverly = CommunityArea.objects.create(name="Beverly", area_id="1")
        lincoln_park = CommunityArea.objects.create(name="Lincoln Park", area_id="2")

        create_permit(beverly, 2021, 1, 15)
        create_permit(beverly, 2021, 2, 20)

        create_permit(lincoln_park, 2021, 3, 10)
        create_permit(lincoln_park, 2021, 2, 14)
        create_permit(lincoln_park, 2021, 6, 22)

        create_permit(lincoln_park, 2025, 4, 6)

        client = APIClient()

        #Act
        response = client.get(reverse("map_data"), {"year": 2021})

        # Assert
        assert response.status_code == 200

        data_by_name = self.get_num_permits_by_name(response)

        assert data_by_name["Beverly"] == 2
        assert data_by_name["Lincoln Park"] == 3

    def test_returns_area_id_in_map_data_response(self, create_permit):
        beverly = CommunityArea.objects.create(name="Beverly", area_id="24")
        create_permit(beverly, 2021, 1, 15)

        client = APIClient()

        response = client.get(reverse("map_data"), {"year": 2021})

        assert response.status_code == 200

        data_by_name = self.get_area_data_by_name(response)

        assert data_by_name["Beverly"]["area_id"] == 24
        assert data_by_name["Beverly"]["num_permits"] == 1

    def test_returns_zero_permits_for_year_outside_ui_filter_range(self, create_permit):
        beverly = CommunityArea.objects.create(name="Beverly", area_id="1")
        lincoln_park = CommunityArea.objects.create(name="Lincoln Park", area_id="2")

        create_permit(beverly, 2021, 1, 15)
        create_permit(beverly, 2023, 2, 20)

        create_permit(lincoln_park, 2021, 3, 10)
        create_permit(lincoln_park, 2020, 2, 14)
        create_permit(lincoln_park, 2019, 6, 22)

        client = APIClient()


        response = client.get(reverse("map_data"), {"year": 2015})


        assert response.status_code == 200

        data_by_name = self.get_num_permits_by_name(response)

        assert data_by_name["Beverly"] == 0
        assert data_by_name["Lincoln Park"] == 0

    def test_returns_zero_when_area_has_no_permits_for_year(self):
        CommunityArea.objects.create(name="Beverly", area_id=1)


        client = APIClient()
        response = client.get(reverse("map_data"), {"year": 2026})


        assert response.status_code == 200

        data_by_name = self.get_num_permits_by_name(response)

        assert data_by_name["Beverly"] == 0

    def test_returns_permit_counts_for_all_years_when_year_is_not_provided(
        self, create_permit
    ):
        beverly = CommunityArea.objects.create(name="Beverly", area_id=1)

        create_permit(beverly, 2021, 1, 15)
        create_permit(beverly, 2025, 2, 20)
        create_permit(beverly, 2026, 3, 10)


        client = APIClient()
        response = client.get(reverse("map_data"))


        assert response.status_code == 200

        data_by_name = self.get_num_permits_by_name(response)

        assert data_by_name["Beverly"] == 3
