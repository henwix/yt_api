from logging import Logger

from django.db.utils import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import orjson
import punq
import stripe
from drf_spectacular.utils import extend_schema

from core.api.v1.payments.serializers import StripeSubscriptionSerializer
from core.apps.payments.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from core.apps.users.converters.users import user_to_entity
from core.project.containers import get_container


# TODO: cache with customer_id invalidation when the user has been deleted
@extend_schema(request=StripeSubscriptionSerializer)
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StripeSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        container: punq.Container = get_container()
        use_case: CreateCheckoutSessionUseCase = container.resolve(CreateCheckoutSessionUseCase)

        try:
            session_url = use_case.execute(
                sub_tier=serializer.validated_data.get('sub_tier'),
                user=user_to_entity(user=request.user),
            )

            return Response(data={'url': session_url})

        except stripe.StripeError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def stripe_webhook_view(request):
    container: punq.Container = get_container()
    logger: Logger = container.resolve(Logger)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    # settings.STRIPE_WEBHOOK_KEY = ''

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=settings.STRIPE_WEBHOOK_KEY,
        )
    except (ValueError, stripe.SignatureVerificationError) as error:
        logger.error(
            'Stripe Webhook SignatureVerificationError',
            extra={'log_meta': orjson.dumps({'error': str(error)})},
        )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        logger.info(session)
        logger.info(user_id)
        # update user.is_premium from metadata

        logger.info(
            'Stripe Webhook Verificated',
            extra={'log_meta': orjson.dumps({'user_id': user_id})},
        )

    else:
        logger.error(
            'Stripe Webhook Unhandled Event Type',
            extra={'log_meta': orjson.dumps({'event_type': event['type']})},
        )

    return Response(status=status.HTTP_200_OK)
