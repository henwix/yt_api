from rest_framework import status


class ErrorCodes:
    REPORT_LIMIT = "report_limit"


ERRORS = {
    ErrorCodes.REPORT_LIMIT: {
        'message': 'You have reached limit of reports to this video. 3 reports by 1 user',
        'status_code': status.HTTP_400_BAD_REQUEST,
    },
}
