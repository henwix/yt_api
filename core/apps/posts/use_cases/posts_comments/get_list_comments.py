from dataclasses import dataclass
from typing import Iterable

from core.apps.posts.models import PostCommentItem
from core.apps.posts.services.comments import BasePostCommentService
from core.apps.posts.services.posts import BasePostService


@dataclass
class GetPostCommentsUseCase:
    post_service: BasePostService
    comment_service: BasePostCommentService

    def execute(self, post_id: str) -> Iterable[PostCommentItem]:
        self.post_service.get_post_by_id_or_404(post_id)

        qs = self.comment_service.get_comments_by_post_id(
            post_id=post_id,
        )

        return qs
