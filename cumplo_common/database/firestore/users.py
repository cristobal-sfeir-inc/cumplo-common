from collections.abc import Generator
from logging import getLogger
from typing import Any

import ulid
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1 import CollectionReference

from cumplo_common.models import User
from cumplo_common.utils.constants import DISABLED_COLLECTION, EMAILS_COLLECTION, KEYS_COLLECTION, USERS_COLLECTION
from cumplo_common.utils.text import secure_key

logger = getLogger(__name__)


class UserCollection:
    collection: CollectionReference
    keys: CollectionReference
    emails: CollectionReference
    client: FirestoreClient

    def __init__(self, client: FirestoreClient) -> None:
        self.collection = client.collection(USERS_COLLECTION)
        self.emails = client.collection(EMAILS_COLLECTION)
        self.keys = client.collection(KEYS_COLLECTION)
        self.client = client

    def _get_by_api_key(self, api_key: str) -> str:
        """Get a user ID by his API key."""
        logger.info(f"Getting user with API key {secure_key(api_key)} from Firestore")
        key = self.keys.document(api_key).get()

        if not key.exists or not (data := key.to_dict()):
            raise KeyError(f"User with API key {secure_key(api_key)} does not exist")

        return data["id_user"]

    def _get_by_email(self, email: str) -> str:
        """Get a user ID by his email."""
        logger.info(f"Getting user with email {email} from Firestore")
        email_doc = self.emails.document(email).get()

        if not email_doc.exists or not (data := email_doc.to_dict()):
            raise KeyError(f"User with email {email} does not exist")

        return data["id_user"]

    def get(self, id_user: str | None = None, api_key: str | None = None, email: str | None = None) -> User:
        """
        Get a user.

        Args:
            id_user (str): The user ID
            api_key (str): The API key
            email (str): The email
        Raises:
            KeyError: When the user does not exist
            ValueError: When the user data is empty or the API key is not valid

        Returns:
            User: The user object containing the user data

        """
        if not (id_user or api_key or email):
            raise ValueError("Either ID, API key or email must be provided")

        if not id_user and api_key:
            id_user = self._get_by_api_key(api_key)

        if not id_user and email:
            id_user = self._get_by_email(email)

        user = self.collection.document(id_user).get()
        if not user.exists or not (data := user.to_dict()):
            raise KeyError(f"User with ID {id_user} does not exist")

        return User(id=ulid.parse(user.id), **data)

    def list(self) -> Generator[User, None, None]:
        """
        List all users.

        Yields:
            Generator[User, None, None]: Iterable of User objects

        """
        logger.info("Getting all users from Firestore")
        for user in self.collection.stream():
            if data := user.to_dict():
                yield User(id=ulid.parse(user.id), **data)

    def create(self, user: User) -> None:
        """
        Create a user.

        Args:
            user (User): The user to be created

        """
        logger.info(f"Creating user {user.id} into Firestore")
        self.collection.document(str(user.id)).set(user.json(exclude={"id"}))
        self.keys.document(user.api_key).set({"id_user": str(user.id)})
        self.emails.document(user.email).set({"id_user": str(user.id)})

    def update(self, user: User, attribute: str) -> None:
        """
        Update a user's attribute.

        Args:
            user (User): The user to be updated
            attribute (str): The attribute to be updated

        """
        logger.info(f"Updating user {user.id} {attribute} into Firestore")
        data = user.json(exclude={"id"})
        update = {attribute: data[attribute]}
        self.collection.document(str(user.id)).update(update)

    def update_notification(self, user: User, id_notification: str) -> None:
        """
        Update a specific user's notification.

        Args:
            user (User): The user to be updated
            id_notification (str): The notification to be updated

        """
        logger.info(f"Updating user {user.id} notification {id_notification} into Firestore")
        data = user.json(exclude={"id"})
        update = {"notifications": {id_notification: data["notifications"][id_notification]}}
        self.collection.document(str(user.id)).update(update)

    def put(self, user: User) -> None:
        """
        Create or updates a user.

        Args:
            user (User): The new user data to be upserted

        """
        logger.info(f"Upserting user {user.id} into Firestore")
        document = self.collection.document(str(user.id))
        document.set(user.json(exclude={"id"}))

    def delete(self, user: User) -> None:
        """
        Delete a user.

        Args:
            user (User): The user to be deleted

        """
        logger.info(f"Deleting user {user.id} from Firestore")
        self.keys.document(user.api_key).delete()
        self.emails.document(user.email).delete()
        self.collection.document(str(user.id)).delete()


class DisabledCollection(UserCollection):
    def __init__(self, client: FirestoreClient, *args: Any, **kwargs: Any) -> None:
        super().__init__(client, *args, **kwargs)
        self.collection = client.collection(DISABLED_COLLECTION)
