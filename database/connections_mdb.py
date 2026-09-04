import asyncio
import logging
import os

import pymongo
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from info import DATABASE_URI, DATABASE_NAME


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ============================================================
# MongoDB Configuration
# ============================================================

if not DATABASE_URI:
    raise RuntimeError(
        "DATABASE_URI is not configured. "
        "Please add DATABASE_URI to your Koyeb environment variables."
    )

if not DATABASE_NAME:
    raise RuntimeError(
        "DATABASE_NAME is not configured. "
        "Please add DATABASE_NAME to your Koyeb environment variables."
    )


# MongoDB connection settings
MONGO_SERVER_SELECTION_TIMEOUT = int(
    os.environ.get("MONGO_SERVER_SELECTION_TIMEOUT", "30000")
)

MONGO_CONNECT_TIMEOUT = int(
    os.environ.get("MONGO_CONNECT_TIMEOUT", "20000")
)

MONGO_SOCKET_TIMEOUT = int(
    os.environ.get("MONGO_SOCKET_TIMEOUT", "30000")
)


# ============================================================
# MongoDB Client
# ============================================================

try:
    myclient = pymongo.MongoClient(
        DATABASE_URI,

        # Connection timeouts
        serverSelectionTimeoutMS=MONGO_SERVER_SELECTION_TIMEOUT,
        connectTimeoutMS=MONGO_CONNECT_TIMEOUT,
        socketTimeoutMS=MONGO_SOCKET_TIMEOUT,

        # Connection stability
        retryWrites=True,
        retryReads=True,

        # Keep connections alive
        maxPoolSize=50,
        minPoolSize=1,

        # TLS is required for mongodb+srv connections.
        tls=True,
    )

    mydb = myclient[DATABASE_NAME]
    mycol = mydb["CONNECTION"]

except Exception:
    logger.exception("Failed to create MongoDB client.")
    raise


# ============================================================
# MongoDB Connection Test
# ============================================================

async def check_mongodb():
    """
    Check whether MongoDB is reachable.

    This runs the blocking PyMongo ping operation in a
    background thread so it does not block the asyncio loop.
    """

    try:
        await asyncio.to_thread(
            myclient.admin.command,
            "ping"
        )

        logger.info("MongoDB connection successful.")
        return True

    except ServerSelectionTimeoutError as e:
        logger.error(
            "MongoDB server selection timeout.\n"
            "Check your DATABASE_URI, MongoDB Atlas cluster, "
            "and Network Access settings.\n"
            "Error: %s",
            e,
        )
        return False

    except PyMongoError as e:
        logger.error(
            "MongoDB connection failed: %s",
            e,
        )
        return False

    except Exception as e:
        logger.exception(
            "Unexpected MongoDB connection error: %s",
            e,
        )
        return False


# ============================================================
# Add Connection
# ============================================================

async def add_connection(group_id, user_id):

    try:
        query = await asyncio.to_thread(
            mycol.find_one,
            {
                "_id": user_id
            },
            {
                "_id": 0,
                "active_group": 0
            }
        )

        if query is not None:

            group_ids = [
                x["group_id"]
                for x in query.get("group_details", [])
            ]

            if group_id in group_ids:
                return False

        group_details = {
            "group_id": group_id
        }

        data = {
            "_id": user_id,
            "group_details": [group_details],
            "active_group": group_id,
        }

        count = await asyncio.to_thread(
            mycol.count_documents,
            {
                "_id": user_id
            }
        )

        if count == 0:

            try:
                await asyncio.to_thread(
                    mycol.insert_one,
                    data
                )

                return True

            except PyMongoError:
                logger.exception(
                    "MongoDB error while inserting connection."
                )
                return False

        else:

            try:
                await asyncio.to_thread(
                    mycol.update_one,
                    {
                        "_id": user_id
                    },
                    {
                        "$push": {
                            "group_details": group_details
                        },
                        "$set": {
                            "active_group": group_id
                        }
                    }
                )

                return True

            except PyMongoError:
                logger.exception(
                    "MongoDB error while updating connection."
                )
                return False

    except Exception:
        logger.exception(
            "Unexpected error in add_connection()."
        )
        return False


# ============================================================
# Active Connection
# ============================================================

async def active_connection(user_id):

    try:

        query = await asyncio.to_thread(
            mycol.find_one,
            {
                "_id": user_id
            },
            {
                "_id": 0,
                "group_details": 0
            }
        )

        if not query:
            return None

        group_id = query.get("active_group")

        if group_id is None:
            return None

        return int(group_id)

    except Exception:
        logger.exception(
            "Unexpected error in active_connection()."
        )
        return None


# ============================================================
# All Connections
# ============================================================

async def all_connections(user_id):

    try:

        query = await asyncio.to_thread(
            mycol.find_one,
            {
                "_id": user_id
            },
            {
                "_id": 0,
                "active_group": 0
            }
        )

        if query is not None:

            return [
                x["group_id"]
                for x in query.get("group_details", [])
            ]

        return None

    except Exception:
        logger.exception(
            "Unexpected error in all_connections()."
        )
        return None


# ============================================================
# Check Active Connection
# ============================================================

async def if_active(user_id, group_id):

    try:

        query = await asyncio.to_thread(
            mycol.find_one,
            {
                "_id": user_id
            },
            {
                "_id": 0,
                "group_details": 0
            }
        )

        return (
            query is not None
            and query.get("active_group") == group_id
        )

    except Exception:
        logger.exception(
            "Unexpected error in if_active()."
        )
        return False


# ============================================================
# Make Connection Active
# ============================================================

async def make_active(user_id, group_id):

    try:

        update = await asyncio.to_thread(
            mycol.update_one,
            {
                "_id": user_id
            },
            {
                "$set": {
                    "active_group": group_id
                }
            }
        )

        return update.modified_count != 0

    except Exception:
        logger.exception(
            "Unexpected error in make_active()."
        )
        return False


# ============================================================
# Make Connection Inactive
# ============================================================

async def make_inactive(user_id):

    try:

        update = await asyncio.to_thread(
            mycol.update_one,
            {
                "_id": user_id
            },
            {
                "$set": {
                    "active_group": None
                }
            }
        )

        return update.modified_count != 0

    except Exception:
        logger.exception(
            "Unexpected error in make_inactive()."
        )
        return False


# ============================================================
# Delete Connection
# ============================================================

async def delete_connection(user_id, group_id):

    try:

        update = await asyncio.to_thread(
            mycol.update_one,
            {
                "_id": user_id
            },
            {
                "$pull": {
                    "group_details": {
                        "group_id": group_id
                    }
                }
            }
        )

        if update.modified_count == 0:
            return False

        query = await asyncio.to_thread(
            mycol.find_one,
            {
                "_id": user_id
            },
            {
                "_id": 0
            }
        )

        if not query:
            return False

        group_details = query.get(
            "group_details",
            []
        )

        if len(group_details) >= 1:

            if query.get("active_group") == group_id:

                previous_group_id = group_details[
                    len(group_details) - 1
                ]["group_id"]

                await asyncio.to_thread(
                    mycol.update_one,
                    {
                        "_id": user_id
                    },
                    {
                        "$set": {
                            "active_group": previous_group_id
                        }
                    }
                )

        else:

            await asyncio.to_thread(
                mycol.update_one,
                {
                    "_id": user_id
                },
                {
                    "$set": {
                        "active_group": None
                    }
                }
            )

        return True

    except Exception:
        logger.exception(
            "Unexpected error in delete_connection()."
        )
        return False


# ============================================================
# Close MongoDB
# ============================================================

async def close_mongodb():

    try:

        await asyncio.to_thread(
            myclient.close
        )

        logger.info(
            "MongoDB connection closed."
        )

    except Exception:
        logger.exception(
            "Error while closing MongoDB."
        )
