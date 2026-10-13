import logging
from typing import Optional, Dict, Any, Tuple
import pymongo
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError, ConnectionFailure

from app.config import settings

logger = logging.getLogger("greenloopai.database")

_mongo_client: Optional[MongoClient] = None
_is_mock: bool = False

def get_client() -> MongoClient:
    global _mongo_client, _is_mock
    if _mongo_client is not None:
        return _mongo_client

    uri = settings.MONGODB_URI.strip()
    if uri.lower() in ("mock", "mongomock", "") or uri.lower().startswith("mock://"):
        try:
            import mongomock
            _mongo_client = mongomock.MongoClient()
            _is_mock = True
            logger.info("Using in-memory MongoMock database for testing.")
            return _mongo_client
        except ImportError:
            logger.warning("mongomock not installed, attempting default localhost mongo")
            uri = "mongodb://localhost:27017"

    try:
        # Real MongoDB Atlas or standard URI
        _mongo_client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000,
            retryWrites=True
        )
        _is_mock = False
        logger.info("Initialized MongoDB client.")
        return _mongo_client
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB client: {e}")
        raise

def get_db():
    client = get_client()
    return client[settings.MONGODB_DATABASE]

def is_mock_db() -> bool:
    return _is_mock

def ping_database() -> Tuple[bool, str]:
    """
    Tests database connectivity with an administrative ping.
    Returns (success: bool, message: str)
    """
    try:
        client = get_client()
        if _is_mock:
            return True, "Connected to in-memory test database"
        
        # Ping the admin database
        res = client.admin.command("ping")
        if res.get("ok") == 1.0:
            return True, "Successfully connected to MongoDB Atlas"
        return False, f"Unexpected ping response: {res}"
    except ConnectionFailure as e:
        return False, f"MongoDB connection failure: {str(e)}"
    except PyMongoError as e:
        return False, f"MongoDB error: {str(e)}"
    except Exception as e:
        return False, f"Database connectivity error: {str(e)}"

def init_indexes():
    """
    Idempotently creates required indexes on collections:
    - users: unique index on normalized email
    - verifications: compound index on (user_id, created_at), unique on id
    - greencoins_transactions: unique index on verification_id (duplicate reward prevention),
      index on (user_id, created_at)
    """
    db = get_db()

    try:
        # 1. users
        db.users.create_index([("email", ASCENDING)], unique=True, name="idx_users_email_unique")
        db.users.create_index([("id", ASCENDING)], unique=True, name="idx_users_id_unique")

        # 2. verifications
        db.verifications.create_index([("id", ASCENDING)], unique=True, name="idx_verifications_id_unique")
        db.verifications.create_index(
            [("user_id", ASCENDING), ("created_at", DESCENDING)],
            name="idx_verifications_user_created"
        )

        # 3. greencoins_transactions
        # Unique index on verification_id prevents duplicate rewards for the same verification
        db.greencoins_transactions.create_index(
            [("verification_id", ASCENDING)],
            unique=True,
            name="idx_transactions_verification_unique"
        )
        db.greencoins_transactions.create_index(
            [("user_id", ASCENDING), ("created_at", DESCENDING)],
            name="idx_transactions_user_created"
        )
        db.greencoins_transactions.create_index([("id", ASCENDING)], unique=True, name="idx_transactions_id_unique")

        logger.info("MongoDB indexes successfully verified.")
    except Exception as e:
        logger.warning(f"Note during index initialization: {e}")

def get_user_balance(user_id: str) -> int:
    """
    Calculates authoritative GreenCoins balance derived from trusted transaction records.
    """
    db = get_db()
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    try:
        results = list(db.greencoins_transactions.aggregate(pipeline))
        if results and "total" in results[0]:
            return int(results[0]["total"])
        return 0
    except Exception as e:
        logger.error(f"Error aggregating GreenCoins balance for user {user_id}: {e}")
        # Fallback to direct Python summation if aggregation operator has issue in mock
        txs = db.greencoins_transactions.find({"user_id": user_id})
        return sum(int(t.get("amount", 0)) for t in txs)
