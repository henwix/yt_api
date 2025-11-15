from logging import Logger

import orjson
import punq
import stripe
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.v1.common.serializers.serializers import DetailOutSerializer, UrlSerializer
from core.api.v1.payments.serializers import StripeSubscriptionInSerializer, StripeSubscriptionStateOutSerializer
from core.api.v1.schema.response_examples.common import build_example_response_from_error
from core.api.v1.schema.response_examples.payments import (
    retrieve_subscription_state_response_example,
    stripe_error_response_example,
)
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.payments.exceptions import StripeSubAlreadyExistsError, StripeSubDoesNotExistError
from core.apps.payments.throttles import CheckoutSessionThrottle
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.payments.use_cases.get_stripe_sub_state import GetStripeSubStateUseCase
from core.apps.payments.use_cases.webhook import StripeWebhookUseCase
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


@extend_schema(
    responses={
        200: OpenApiResponse(
            response=StripeSubscriptionStateOutSerializer,
            description='Subscription state retrieved',
        ),
        404: OpenApiResponse(
            response=DetailOutSerializer,
            description='Subscription does not exist',
        ),
        500: OpenApiResponse(
            response=DetailOutSerializer,
            description='Stripe 500 error',
        ),
    },
    examples=[
        retrieve_subscription_state_response_example(),
        build_example_response_from_error(error=StripeSubDoesNotExistError),
        stripe_error_response_example(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR, value='An error occured while retrieving subscription state'
        ),
    ],
    summary='Get subscription state',
)
class GetStripeSubStateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        container: punq.Container = get_container()
        logger: Logger = container.resolve(Logger)
        use_case: GetStripeSubStateUseCase = container.resolve(GetStripeSubStateUseCase)

        try:
            result = use_case.execute(user=user_to_entity(user=request.user))

        except stripe.StripeError as error:
            logger.error(
                'Stripe Error has been raised in GetStripeSubStateView',
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': 'An error occured while retrieving subscription state'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(data=result, status=status.HTTP_200_OK)


@extend_schema(
    request=StripeSubscriptionInSerializer,
    responses={
        201: OpenApiResponse(
            response=UrlSerializer,
            description='Checkout session created',
        ),
        400: OpenApiResponse(
            response=DetailOutSerializer,
            description='Subscription already exists',
        ),
        500: OpenApiResponse(
            response=DetailOutSerializer,
            description='Stripe 500 error',
        ),
    },
    examples=[
        build_example_response_from_error(error=StripeSubAlreadyExistsError),
        stripe_error_response_example(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR, value='An error occured while creating a checkout session'
        ),
    ],
    summary='Create checkout session',
)
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CheckoutSessionThrottle]

    def post(self, request):
        serializer = StripeSubscriptionInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        container: punq.Container = get_container()
        logger: Logger = container.resolve(Logger)
        use_case: CreateCheckoutSessionUseCase = container.resolve(CreateCheckoutSessionUseCase)

        try:
            session_url = use_case.execute(
                sub_tier=serializer.validated_data.get('sub_tier'),
                user=user_to_entity(user=request.user),
            )

        except stripe.StripeError as error:
            logger.error(
                'Stripe Error has been raised in CreateCheckoutSessionView',
                extra={'log_meta': orjson.dumps(str(error)).decode()},
            )
            return Response(
                {'detail': 'An error occured while creating a checkout session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(data={'url': session_url}, status=status.HTTP_201_CREATED)


@extend_schema(summary='Stripe Webhook')
@csrf_exempt
@api_view(['POST'])
def stripe_webhook_view(request):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)
    use_case: StripeWebhookUseCase = container.resolve(StripeWebhookUseCase)

    try:
        use_case.execute(
            payload=request.body,
            signature=request.META.get('HTTP_STRIPE_SIGNATURE'),
        )

    except stripe.StripeError as error:
        logger.error(
            'Stripe Error has been raised in stripe_webhook_view',
            extra={'log_meta': orjson.dumps(str(error)).decode()},
        )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    except ServiceException as error:
        logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)
