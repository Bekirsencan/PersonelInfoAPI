
from flask import Flask,request ### POST isteklerinde gelen body'i almak için gerekli olan kütüphane
from flask_restful import Api ### API yazmak için gerekli olan kütüphane
import database ### database.py dosyası
from user_profile import *

app = Flask(__name__)
api = Api(app)
user_id = 1

###Genel Bilgi
### Procfile adlı dosya Web Hosting Server olarak kullandığımız Heroku için gerekli olan dosyadır.

_user_profile = user_profile()
### Client giriş yaparken uygulama üzerinden bu Route'a Get isteği atılır. Bu istek ile database.py dosyasındaki ilgili fonksiyon çalışır.
@app.route('/login_api/<string:username>/<string:password>', methods = ['GET'])
def login(username,password):
    return _user_profile.user_login(username,password)

### Client profiline tıkladığında bu Route'a Get isteği atar. Bu istek ile database.py dosyasındaki ilgili fonksiyon çalışır.
@app.route('/onclick_profile_api/<string:objectid>',methods = ['GET'])
def onclick_profile(objectid):
    return _user_profile.get_profile(ObjectId(objectid))

### Giriş yapan kullanıcının departmanına göre o departmandaki tüm kullanıcılar listelenirken bu Route'a Get isteği atılır.
@app.route('/query/<string:department_name>',methods=['GET'])
def query(department_name):
    return database.query_by_department_name(department_name)

### Client profilinde kendi sosyal medya hesaplarını görmek istersen bu Route'a Get isteği atılır.
@app.route('/social/<string:objectid>',methods=['GET'])
def social(objectid):
    return database.get_social(objectid)

### Yeni bir kullanıcı oluşturulmak istendiğinde Client'ın tüm bilgileri bu Route'a bir body ile POST isteği atılır.
@app.route('/register',methods=['POST'])
def register():
    global user_id
    user_id +=1
    data = request.get_json()
    return database.insert_profile(
        user_id,
        data['profile_picture_url'],
        data['username'],
        data['password'],
        data['name_surname'],
        data['gender'],
        data['job_info'],
        data['contact']
    )
    

### Client bilgilerini güncellemek istediği zaman bu Route'a Post isteği atar. Burada URL'de bulunan update_name değişkeni ile update_by_arg() fonksiyonu çalışır.
@app.route('/update/<string:update_name>',methods=['POST'])
def udpate(update_name):
    data = request.get_json()
    return update_by_arg(update_name,data['_id'],data)



### Bu fonksiyon ile 4 farklı güncelleme işlemi için 4 farklı API yazmak yerine 1 fonksiyon üzerinden hangi güncelleme işleminin yapılacağı seçiliyor.
### update_name değişkeni güncellenecek collection'ı belirtir. switcher üzerinde update_name değişkenine göre fonksiyonlar çalıştırılır.
def update_by_arg(update_name,objectid,data):
    switcher = {
        'status':lambda:database.update_status(objectid,data),
        'profile':lambda:database.update_profile(objectid,data),
        'job_info':lambda:database.update_job_info(objectid,data),
        'social':lambda:database.update_social(objectid,data)
        }
    return switcher.get(update_name,lambda:'Invalid')()


if __name__ == "__main__":
    app.run(debug = True)