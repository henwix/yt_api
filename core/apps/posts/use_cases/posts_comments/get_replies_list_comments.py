from collections.abc import Iterable
from dataclasses import dataclass

from core.apps.posts.models import PostCommentItem
from core.apps.posts.services.comments import BasePostCommentService


@dataclass
class GetPostCommentRepliesUseCase:
    post_service: BasePostCommentService

    def execute(self, comment_id: int) -> Iterable[PostCommentItem]:
        return self.post_service.get_replies_by_comment_id(comment_id=comment_id)
