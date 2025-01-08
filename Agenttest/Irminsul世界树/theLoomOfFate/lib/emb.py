
from xinference.client import Client
from typing import List, Optional


class XinferenceEmbeddings():
    def __init__(
        self, server_url: Optional[str] = None, model_name: Optional[str] = None
    ):
        try:
            from xinference.client import Client
        except ImportError as e:
            raise ImportError(
                "不存在xinference客户端"
                "使用`pip install xinference` 或 `pip install xinference_client`进行安装"
            ) from e
            
        super().__init__()
        if server_url is None:
            raise ValueError("请提供xinference server URL")
        if model_name is None:
            raise ValueError("请提供xinference model UID")
        self.endpoint = server_url
        self.model_name = model_name
        self.client = Client(server_url)
        
    def launchEmb(self):
        client = Client(self.endpoint)
        client.launch_model(
            model_name=self.model_name,
            model_uid=self.model_name,
            model_type="embedding",
        )
        print(f"successfully launchEmb:{self.model_name}")
            
    def shutDownEmb(self):
        client = Client(self.endpoint)
        client.terminate_model(model_uid=self.model_name)
        print(f"successfully shutDownEmb:{self.model_name}")

    def embedDocuments(self,texts: List[str]) -> List[List[float]]:
        client = Client(self.endpoint)
        model = client.get_model(model_uid=self.model_name)
        embeddings = [
                model.create_embedding(text)["data"][0]["embedding"] for text in texts
            ]
        print(f"successfully Embbed:{texts}")
        return [list(map(float, e)) for e in embeddings]
        
            





