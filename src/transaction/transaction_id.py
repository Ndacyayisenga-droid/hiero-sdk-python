import time
from src.proto import basic_types_pb2, timestamp_pb2
from src.account.account_id import AccountId
import random

class TransactionId:
    """
    Represents the unique identifier for a transaction.

    A TransactionId consists of an AccountId and a valid start timestamp.
    It ensures uniqueness for each transaction initiated by an account.

    Attributes:
        account_id (AccountId): The AccountId of the transaction's initiator.
        valid_start (Timestamp): The valid start time of the transaction.
    """

    def __init__(self, account_id: AccountId, valid_start: timestamp_pb2.Timestamp):
        """
        Initializes a TransactionId with the given account ID and valid start timestamp.

        Args:
            account_id (AccountId): The account ID initiating the transaction.
            valid_start (Timestamp): The valid start time of the transaction.
        """
        self.account_id = account_id
        self.valid_start = valid_start

    @classmethod
    def generate(cls, account_id: AccountId):
        """
        Generates a new TransactionId using the current time as the valid start,
        subtracting a random number of seconds to adjust for potential network delays.

        Args:
            account_id (AccountId): The account ID initiating the transaction.

        Returns:
            TransactionId: A new TransactionId instance.
        """
        cut_off_seconds = random.randint(5, 8) # subtract random number of seconds between 5 and 8
        adjusted_time = time.time() - cut_off_seconds
        seconds = int(adjusted_time)
        nanos = int((adjusted_time - seconds) * 1e9)
        valid_start = timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)
        return cls(account_id, valid_start)

    @classmethod
    def from_string(cls, transaction_id_str: str):
        """
        Parses a TransactionId from a string in the format 'account_id@seconds.nanos'.

        Args:
            transaction_id_str (str): The string representation of the TransactionId.

        Returns:
            TransactionId: A new TransactionId instance.

        Raises:
            ValueError: If the input string is not in the correct format.
        """
        try:
            account_id_str, timestamp_str = transaction_id_str.split('@')
            account_id = AccountId.from_string(account_id_str)
            seconds_str, nanos_str = timestamp_str.split('.')
            valid_start = timestamp_pb2.Timestamp(seconds=int(seconds_str), nanos=int(nanos_str))
            return cls(account_id, valid_start)
        except Exception as e:
            raise ValueError(f"Invalid TransactionId string format: {transaction_id_str}") from e

    def to_string(self) -> str:
        """
        Returns the string representation of the TransactionId in the format 'account_id@seconds.nanos'.

        Returns:
            str: The string representation of the TransactionId.
        """
        return f"{self.account_id}@{self.valid_start.seconds}.{self.valid_start.nanos}"

    def to_proto(self) -> basic_types_pb2.TransactionID:
        """
        Converts the TransactionId to its protobuf representation.

        Returns:
            TransactionID: The protobuf TransactionID object.
        """
        transaction_id_proto = basic_types_pb2.TransactionID()
        transaction_id_proto.accountID.CopyFrom(self.account_id.to_proto())
        transaction_id_proto.transactionValidStart.CopyFrom(self.valid_start)
        return transaction_id_proto

    @classmethod
    def from_proto(cls, transaction_id_proto: basic_types_pb2.TransactionID):
        """
        Creates a TransactionId instance from a protobuf TransactionID object.

        Args:
            transaction_id_proto (TransactionID): The protobuf TransactionID object.

        Returns:
            TransactionId: A new TransactionId instance.
        """
        account_id = AccountId.from_proto(transaction_id_proto.accountID)
        valid_start = transaction_id_proto.transactionValidStart
        return cls(account_id, valid_start)

    def __eq__(self, other):
        """
        Checks if this TransactionId is equal to another.

        Args:
            other (TransactionId): The other TransactionId to compare.

        Returns:
            bool: True if equal, False otherwise.
        """
        return (
            isinstance(other, TransactionId) and
            self.account_id == other.account_id and
            self.valid_start.seconds == other.valid_start.seconds and
            self.valid_start.nanos == other.valid_start.nanos
        )

    def __hash__(self):
        """
        Returns the hash of the TransactionId.

        Returns:
            int: The hash value.
        """
        return hash((self.account_id, self.valid_start.seconds, self.valid_start.nanos))

    def __str__(self):
        """
        Returns the string representation of the TransactionId.

        Returns:
            str: The string representation.
        """
        return self.to_string()
