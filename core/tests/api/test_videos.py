from rest_framework.test import APIClient

import pytest


@pytest.mark.django_db
def test_video_creation(client: APIClient, jwt: str):
    """Test video created after POST request to endpoint: /api/v1/video/"""

    client.credentials(HTTP_AUTHORIZATION=jwt)

    payload = {
        'name': 'Pre-Party Set at a Bali Hideaway',
        'description': 'Test video description. Yeah, this is description.',
        'status': 'PUBLIC',
    }

    response = client.post('/api/v1/video/', payload)

    assert response.status_code == 201
    assert response.data.get('name') == payload.get('name')
    assert response.data.get('description') == payload.get('description')
    assert response.data.get('status') == payload.get('status')


@pytest.mark.skip('not implemented')
def test_video_retrieved(client: APIClient): ...
