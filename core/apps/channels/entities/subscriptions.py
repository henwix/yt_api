from dataclasses import dataclass
from datetime import datetime


@dataclass
class SubscriptionItemEntity:
    id: int
    subscriber_id: int
    subscribed_to_id: int
    created_at: datetime
