from pymongo import MongoClient

def setup_mongo_db(uri, db_name):
    """
    Sets up a connection to MongoDB and returns the database instance.

    :param uri: MongoDB connection string
    :param db_name: Name of the database to connect to
    :return: Database instance
    """
    try:
        # Create a MongoDB client
        client = MongoClient(uri)
        
        # Access the specified database
        db = client[db_name]
        
        print(f"Connected to MongoDB database: {db_name}")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace with your MongoDB connection string and database name
    mongo_uri = "mongodb://localhost:27017/"
    database_name = "admin_db"
    
    db = setup_mongo_db(mongo_uri, database_name)
    if db:
        # Perform database operations here
        pass