import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.store_agent import StoreAgent
from src.database.milvus_db import MilvusVectorDatabase

def generate_sample_text():
    # Use absolute path relative to the examples directory
    #dummy_file = "healthcare_data/hospital_data.txt"
    dummy_file = "dummy_file.txt"
    with open(dummy_file, "r") as file:
        return file.read()


if __name__ == "__main__":
    milvus_db = MilvusVectorDatabase()
    milvus_db.connect()
    milvus_db.create_collection("test_collection")

    sample_text = generate_sample_text()
    store_agent = StoreAgent(postgres_db=None, milvus_db=milvus_db)

    store_agent.classify_and_store_query(sample_text)

