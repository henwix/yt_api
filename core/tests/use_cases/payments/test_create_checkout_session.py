# import pytest
#
# from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
#
#
# @pytest.mark.parametrize(
#     argnames='expected_url',
#     argvalues=[
#         'https://example.com/checkout_url/1231242552',
#         'https://example.com/checkout_url/829929839823',
#         'https://example.com/checkout_url/asfjkhsafk10',
#         'https://example.com/checkout_url/929299292922',
#     ],
# )
# def test_checkout_session_created(
#     create_checkout_session_use_case: CreateCheckoutSessionUseCase,
#     expected_url: str,
# ):
#     create_checkout_session_use_case.stripe_service.stripe_provider.expected_checkout_session_url = expected_url
#
#     create_checkout_session_use_case.execute()
