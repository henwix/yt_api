from rest_framework import status


class ErrorCodes:
    POST_AUTHOR_SLUG_NOT_PROVIDED = "post_author_slug_not_provided"
    POST_NOT_FOUND = "post_not_found"
    POST_LIKE_NOT_FOUND = "post_like_not_found"


ERRORS = {
    ErrorCodes.POST_AUTHOR_SLUG_NOT_PROVIDED: {
        'message': "'s' query-parameter was not provided",
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.POST_NOT_FOUND: {
        'message': 'Post not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.POST_LIKE_NOT_FOUND: {
        'message': 'Post like not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
}
