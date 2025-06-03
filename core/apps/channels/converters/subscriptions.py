from core.apps.channels.entities.subscriptions import SubscriptionItemEntity
from core.apps.channels.models import SubscriptionItem


def sub_from_entity(subscription: SubscriptionItemEntity) -> SubscriptionItem:
    return SubscriptionItem(
        pk=subscription.id,
        subscriber_id=subscription.subscriber_id,
        subscribed_to_id=subscription.subscribed_to_id,
        created_at=subscription.created_at,
    )


def sub_to_entity(subscription: SubscriptionItem) -> SubscriptionItemEntity:
    return SubscriptionItemEntity(
        id=subscription.pk,
        subscriber_id=subscription.subscriber_id,
        subscribed_to_id=subscription.subscribed_to_id,
        created_at=subscription.created_at,
    )
