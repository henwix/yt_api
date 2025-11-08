import base64

import pytest

from core.apps.common.services.encoding import BaseEncodingService


@pytest.mark.parametrize(
    argnames='data',
    argvalues=[123456, 'test_data', 'data_to_encode', 8427424, 'Data123_To_Encode_test'],
)
def test_value_encoded(encoding_service: BaseEncodingService, data: int | str):
    """Test that data has been encoded successfully."""

    # convert data to bytes for using with base64
    data_bytes = str(data).encode(encoding='utf-8') if isinstance(data, int) else data.encode(encoding='utf-8')

    # encode via service
    encoded_value = encoding_service.base64_encode(data=data)

    # encode via base64
    expected_value = base64.b64encode(data_bytes).decode(encoding='utf-8').strip('=')

    assert expected_value == encoded_value


@pytest.mark.parametrize(
    argnames='data',
    argvalues=[8758375, 'data_for_test', 'encode_data', 222184595, 'Data_222_to_Encode_333'],
)
def test_value_decoded(encoding_service: BaseEncodingService, data: int | str):
    """Test that data has been decoded successfully."""

    encoded_value = encoding_service.base64_encode(data=data)
    decoded_value = encoding_service.base64_decode(data=encoded_value)

    assert decoded_value == str(data)
