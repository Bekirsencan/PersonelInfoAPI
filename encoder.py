
from users import Users
import json ### json format için gerekli olan kütüphane
from bson import ObjectId ### objectid için gerekli olan kütüphane

### MongoDB üzerinde her bir collection unique olan objectid ile tutulur. Bu objectid 24 adet harf veya rakamdan oluşur. Python IDE'ler bu objectid yi
### encode ve decode ederekn kullanır. Bu class ise bizim objectid encoderımız olarak görev yapıyor. Bu class sayesinde MongoDB üzerindeki objectid lere erişim sağlayabiliyorum.
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


a = Users()
a.username



