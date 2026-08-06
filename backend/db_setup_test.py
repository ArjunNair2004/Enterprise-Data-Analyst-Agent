import json
import chromadb

def build_vector_db():
    # 1. Load the updated schema JSON
    print("Reading data_dictionary.json...")
    with open("data_dictionary.json", "r") as f:
        schema_data = json.load(f)

    documents = []
    metadatas = []
    ids = []

    # Handle both list format and object format
    tables = schema_data.get("tables", schema_data if isinstance(schema_data, list) else [])

    # 2. Extract and format table information for embedding
    for table in tables:
        table_name = table["table_name"]
        description = table.get("description", "")
        
        # Format columns list
        columns_info = []
        for col in table.get("columns", []):
            columns_info.append(f"- {col['name']} ({col['type']}): {col['description']}")
        columns_text = "\n".join(columns_info)
        
        # Format business logic rules
        rules = table.get("business_logic_rules", table.get("business_rules", []))
        if isinstance(rules, list):
            rules_text = "\n".join([f"- {rule}" for rule in rules])
        else:
            rules_text = str(rules)

        # Build full text payload for the table
        doc_content = (
            f"Table Name: {table_name}\n"
            f"Description: {description}\n\n"
            f"Columns:\n{columns_text}\n\n"
            f"Business Rules:\n{rules_text}"
        )

        documents.append(doc_content)
        metadatas.append({"table_name": table_name})
        ids.append(f"schema_{table_name}")

    # 3. Initialize local persistent ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")

    # Clear previous schema collection if it exists
    try:
        client.delete_collection(name="schema_store")
        print("Cleared existing ChromaDB schema collection.")
    except Exception:
        pass

    # Create new collection and insert documents
    collection = client.create_collection(name="schema_store")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Success! Indexed {len(documents)} table schema(s) into ChromaDB at './chroma_db'.")

if __name__ == "__main__":
    build_vector_db()