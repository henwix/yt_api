from drf_spectacular.utils import OpenApiParameter


def video_id_openapi_parameter() -> OpenApiParameter:
    return OpenApiParameter(
        name='v',
        description='Parameter identifying video id',
        required=True,
        type=str,
    )
