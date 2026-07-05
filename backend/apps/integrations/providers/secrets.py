import abc

class BaseSecretsProvider(abc.ABC):
    @abc.abstractmethod
    def get_secret(self, reference: str) -> str:
        pass

    @abc.abstractmethod
    def store_secret(self, reference: str, secret: str) -> bool:
        pass

class LocalEncryptedSecretsProvider(BaseSecretsProvider):
    """
    Dummy implementation for Sprint 13.
    In a real environment, this would use a Key Management Service (KMS)
    or django-cryptography to securely store and retrieve the token.
    """
    def __init__(self):
        self._mock_storage = {}

    def get_secret(self, reference: str) -> str:
        return self._mock_storage.get(reference, "")

    def store_secret(self, reference: str, secret: str) -> bool:
        self._mock_storage[reference] = secret
        return True
