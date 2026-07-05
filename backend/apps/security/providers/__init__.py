import abc
from typing import Any, Dict


class BaseMFAProvider(abc.ABC):
    """Abstract MFA provider (e.g. TOTP, SMS, Email)."""
    @abc.abstractmethod
    def generate_challenge(self, user_id: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def verify_challenge(self, user_id: str, challenge_id: str, code: str) -> bool:
        pass


class BaseSecretsProvider(abc.ABC):
    """Abstract provider for enterprise secret management (e.g. HashiCorp Vault, AWS Secrets Manager)."""
    @abc.abstractmethod
    def store_secret(self, path: str, secret_value: str) -> str:
        pass

    @abc.abstractmethod
    def retrieve_secret(self, reference: str) -> str:
        pass

    @abc.abstractmethod
    def revoke_secret(self, reference: str) -> None:
        pass


class BaseEncryptionProvider(abc.ABC):
    """Abstract provider for field-level encryption/decryption."""
    @abc.abstractmethod
    def encrypt(self, plaintext: str) -> str:
        pass

    @abc.abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        pass


class BaseOAuthProvider(abc.ABC):
    """Abstract OAuth/OIDC provider for SSO integration."""
    @abc.abstractmethod
    def get_authorization_url(self) -> str:
        pass

    @abc.abstractmethod
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        pass

__all__ = [
    "BaseMFAProvider",
    "BaseSecretsProvider",
    "BaseEncryptionProvider",
    "BaseOAuthProvider",
]
