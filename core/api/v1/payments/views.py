from logging import Logger

import orjson
import punq
import stripe
from django.core.cache import cache
from django.db.utils import settings
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.v1.payments.serializers import StripeSubscriptionInSerializer
from core.apps.common.exceptions.exceptions import ServiceException
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.payments.use_cases.webhook import StripeWebhookUseCase
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def stripe_sub_state(request):
    user_id = request.user.pk
    customer_id = cache.get(f'stripe:user:{user_id}')
    sub_data = cache.get(f'stripe:customer:{customer_id}')
    if customer_id:
        cached_value = cache.get(f'portal:{customer_id}')
        if cached_value:
            sub_data['customer_portal'] = cached_value
        else:
            session = stripe.billing_portal.Session.create(
                api_key=settings.STRIPE_SECRET_KEY,
                customer=customer_id,
            )
            sub_data['customer_portal'] = session.url
            cache.set(f'portal:{customer_id}', session.url, 60 * 1)
    return Response(data=sub_data)


# TODO: cache with customer_id invalidation when the user has been deleted
@extend_schema(request=StripeSubscriptionInSerializer)
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

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
                extra={'log_meta': orjson.dumps(error).decode()},
            )
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        except ServiceException as error:
            logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
            raise

        return Response(data={'url': session_url})


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
            extra={'log_meta': orjson.dumps(error).decode()},
        )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    except ServiceException as error:
        logger.error(error.message, extra={'log_meta': orjson.dumps(error).decode()})
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)
