import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_channel_patch_data(client: APIClient, jwt_access: str):
    """Test GET request to retrieve channel's data. Status code should be 200"""
    client.credentials(HTTP_AUTHORIZATION=jwt_access)
    response = client.get('/api/v1/channel/')

    assert response.status_code == 200
