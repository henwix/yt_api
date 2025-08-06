from rest_framework import status


class ErrorCodes:
    # videos/exceptions/playlists.py
    PLAYLIST_ID_NOT_PROVIDED = "playlist_id_not_provided"
    PLAYLIST_NOT_FOUND = "playlist_not_found"
    VIDEO_NOT_IN_PLAYLIST = "video_not_in_playlist"
    PLAYLIST_PERMISSION_ERROR = "playlist_permission_error"

    # videos/exceptions/upload.py
    VIDEO_NOT_FOUND_BY_KEY = "video_not_found_by_key"
    VIDEO_NOT_FOUND_BY_UPLOAD_ID = "video_not_found_by_upload_id"
    VIDEO_FILENAME_NOT_PROVIDED = "video_filename_not_provided"
    VIDEO_FILENAME_FORMAT_ERROR = "video_filename_format_error"

    # videos/exceptions/videos.py
    VIDEO_NOT_FOUND_BY_VIDEO_ID = "video_not_found_by_video_id"
    VIDEO_ID_NOT_PROVIDED = "video_id_not_provided"
    VIDEO_NOT_FOUND_IN_HISTORY = "video_not_found_in_history"
    VIDEO_LIKE_NOT_FOUND = "video_like_not_found"
    VIEW_EXISTS = "view_exists"
    VIDEO_AUTHOR_NOT_MATCH = "video_author_not_match"
    PRIVATE_VIDEO_PERMISSION_ERROR = "private_video_permission"
    PRIVATE_VIDEO_OR_UPLOADING = "private_video_or_uploading"


ERRORS = {
    # videos/exceptions/playlists.py
    ErrorCodes.PLAYLIST_ID_NOT_PROVIDED: {
        'message': "'playlist_id' parameter was not provided",
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.PLAYLIST_NOT_FOUND: {
        'message': 'Playlist not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.VIDEO_NOT_IN_PLAYLIST: {
        'message': 'Video does not exist in playlist',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.PLAYLIST_PERMISSION_ERROR: {
        'message': 'You do not have permission to perform actions with this playlist',
        'status_code': status.HTTP_403_FORBIDDEN,
    },

    # videos/exceptions/upload.py
    ErrorCodes.VIDEO_NOT_FOUND_BY_KEY: {
        'message': 'Video not found by key',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.VIDEO_NOT_FOUND_BY_UPLOAD_ID: {
        'message': 'Video not found by upload id',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.VIDEO_FILENAME_NOT_PROVIDED: {
        'message': 'Video filename was not provided',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.VIDEO_FILENAME_FORMAT_ERROR: {
        'message': 'Unsupported video file format',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },

    # videos/exceptions/videos.py
    ErrorCodes.VIDEO_NOT_FOUND_BY_VIDEO_ID: {
        'message': 'Video not found by video_id',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.VIDEO_ID_NOT_PROVIDED: {
        'message': '"video_id" was not provided',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.VIDEO_NOT_FOUND_IN_HISTORY: {
        'message': 'Video does not exist in history',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.VIDEO_LIKE_NOT_FOUND: {
        'message': 'Video like/dislike not found',
        'status_code': status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.VIEW_EXISTS: {
        'message': 'View already exists, you can add 1 view per 24h',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.VIDEO_AUTHOR_NOT_MATCH: {
        'message': 'Video author does not match the current user',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.PRIVATE_VIDEO_PERMISSION_ERROR: {
        'message': 'You do not have permission to access this video',
        'status_code': status.HTTP_403_FORBIDDEN,
    },
    ErrorCodes.PRIVATE_VIDEO_OR_UPLOADING: {
        'message': "You can't perform actions if the video is private or still uploading",
        'status_code': status.HTTP_403_FORBIDDEN,
    },
}
