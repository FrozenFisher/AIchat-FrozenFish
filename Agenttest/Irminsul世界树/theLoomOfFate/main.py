from lib.emb import XinferenceEmbeddings
import chromadb


database = ["This is a document about engineer", "This is a document about steak"]
databaseClient = chromadb.PersistentClient(path="/Users/ycc/workspace/Chat/collection/Agenttest/Irminsul世界树/data/middleTermMem")

emb = XinferenceEmbeddings(
    server_url="http://0.0.0.0:9997",
    model_name="bge-large-zh-v1.5",
)

emb.launchEmb()
embbedDoc = emb.embedDocuments(database)

collection = databaseClient.get_or_create_collection(name="middleTermMem")
collection.update(
    embeddings=embbedDoc,
    documents=database,
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
    )

query_texts = ["Which food is the best?"]

results = collection.query(
    query_embeddings=emb.embedDocuments(query_texts),
    n_results=2
)
print(results["documents"])


emb.shutDownEmb()