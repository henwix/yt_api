import punq
from django.db.models.signals import post_delete
from django.dispatch import receiver

from core.apps.users.models import CustomUser
from core.apps.users.use_cases.users.user_invalidate_stripe_cache import UserInvalidateStripeCacheUseCase
from core.project.containers import get_container


@receiver(signal=[post_delete], sender=CustomUser)
def user_invalidate_stripe_cache(instance: CustomUser, **kwargs):
    container: punq.Container = get_container()
    use_case: UserInvalidateStripeCacheUseCase = container.resolve(UserInvalidateStripeCacheUseCase)
    use_case.execute(user_id=instance.pk)
