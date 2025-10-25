from enum import Enum

from django.db import models
from drf_spectacular.utils import OpenApiParameter


def build_enum_query_param(
    name: str,
    enum: type[models.TextChoices] | type[Enum],
    description: str = '',
    required: bool = False,
) -> OpenApiParameter:
    """Build query parameter with detailed description based on provided
    Enum."""

    desc_list = '\n'.join([f'- `{i.value}` — {i.label}' for i in enum])

    return OpenApiParameter(
        name=name,
        location=OpenApiParameter.QUERY,
        required=required,
        type=str,
        enum=enum,
        description=f'{description}\n\n{desc_list}',
    )
