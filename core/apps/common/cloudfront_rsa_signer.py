from django.conf import settings

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from cryptography.hazmat.primitives.asymmetric import padding


def rsa_signer(message):
    # Set key from settings to variable
    private_key_pem = settings.AWS_CLOUDFRONT_KEY

    # Load key in object
    private_key = serialization.load_pem_private_key(
        data=private_key_pem,
        password=None,
        backend=default_backend(),
    )

    # Sign message
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())  # noqa: DUO134
