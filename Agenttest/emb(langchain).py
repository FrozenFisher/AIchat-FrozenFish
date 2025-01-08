from langchain_community.embeddings import XinferenceEmbeddings

emb = XinferenceEmbeddings(
    server_url="http://0.0.0.0:9997",
    model_uid="bge-large-zh-v1.5"
)

query_result1 = emb.embed_query("This is a test query")
query_result2 = emb.embed_documents(["text A","text B"])

print(query_result1,"/n",query_result2)