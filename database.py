from flask.json import jsonify ### Verileri JSON formatında geri döndürmek için gerekli kütüphane
from encoder import JSONEncoder ### encoder.py dosyasındaki Encoder ı kullanmak için gereklidir.
from pymongo import MongoClient,cursor  ### MongoDB bağlantıs için gerekli kütüphane
from bson.objectid import ObjectId ### objectid için gerekli olan kütüphane
from flask import Response ### API'a gelen isteklerde response döndürmek için gerekli olan kütüphane


client = MongoClient("mongodb+srv://bekirsencan:Turtoise@cluster0.vfdtl.mongodb.net/PersonelAPP?retryWrites=true&w=majority")### MongoDB  bağlantısı oluşturdum.
current_database = client['PersonelAPP']### MongoDB üzerinde hangi veritabanını kullanacağımı belirttim.



### GET REQUEST

### Client login işlemi sonucunda bu fonksiyon çalışıyor. Client username ve password kontrolü sağlanıyor. Giriş doğru ise get_profile() fonksiyonu çalışıyor.
def check_user(username,password):
    for data in current_database["Profile"].find({'$and':[{'username':username},{'password':password}]},{'_id':1}):
        return  get_profile(data["_id"]) 

### Client başarılı giriş yaptığında bu fonksiyon çalışır. Bu fonksiyon ile veritabanından kullanıcının bilgileri uygulamaya gönderilir.
def get_profile(objectid):
    for data in current_database["Profile"].aggregate([{'$match':{'_id':ObjectId(objectid)}},
                                              {'$lookup':{'from':"Job_Info",'localField':"_id",'foreignField':"_id",'as':"job_info"}},
                                              {'$lookup':{'from':"Contact",'localField':"_id",'foreignField':"_id",'as':"contact"}},
                                              {'$lookup':{'from':"Status",'localField':"_id",'foreignField':"_id",'as':"status"}}]):
        result = JSONEncoder().encode(data)
        return Response(result,mimetype='application/json') ###  Yapıldı
    
### Client uygulama üzerinde profiline gitmek istediği zaman bu fonksiyon çalışır. Geri dönüş olarak Client'ın profilde ihtiyacı olan veriler döner.
def onclick_profile(objectid):
    for data in current_database["Profile"].aggregate([{'$match':{'_id':ObjectId(objectid)}},
                                              {'$lookup':{'from':"Job_Info",'localField':"_id",'foreignField':"_id",'as':"job_info"}},
                                              {'$unwind':'$job_info'},
                                              {'$lookup':{'from':"Contact",'localField':"_id",'foreignField':"_id",'as':"contact"}},
                                              {'$unwind':'$contact'}
                                              ]):
        result = JSONEncoder().encode(data)
        return Response(result,mimetype='application/json')

### Client'ın eğer ekleme yaptıysa sosyal medya linkleri döner. Eğer ekleme yapılmadıysa boş döner.
def get_social(objectid):
    result = []
    for data in current_database["Social"].find({'_id':ObjectId(objectid)},{'_id':0}):
        result.append(data['social'][0])
        result.append(data['social'][1])
    return jsonify(result)


### POST REQUEST

### Yeni kayıt oluştururken bu fonksiyon kullanılır. Bu fonksiyon ile ilk önce profil veritabanına eklenir. Ardından MongoDB ye özel her bir collection için
### unique olan objectid'yi alıp kullanıcının diğer verilerini eklemek için kullanıyorum. Bu referans ile veritabanı oluşturmama olanak veriyor. Bunların ardından 
### insert_job_info(),insert_status(),insert_social(),insert_contact() fonksiyonları çalışır.
def insert_profile(user_id,profile_picture_url,username,password,name_surname,gender,job_info,contact):
    current_database["Profile"].insert(
        {'user_id':user_id,
         'profile_picture_url':profile_picture_url,
         'username':username,
         'password':password,
         'name_surname':name_surname,
         'gender':gender}
        )
    for data in current_database["Profile"].find({'$and':[{'username':username},{'password':password}]},{'_id':1}):
        insert_job_info(
            data["_id"],
            job_info[0]['company_name'],
            job_info[0]['department_name'],
            job_info[0]['job'],
            job_info[0]['about'])
        insert_status(data["_id"])
        insert_social(data["_id"])
        insert_contact(
            data["_id"],
            contact[0]['email'],
            contact[0]['number']
            )
        return "200"

### Client kayıt olduğunda iş bilgileri burada veritabanına aktarılır.
def insert_job_info(_id,company_name,department_name,job,about):
    current_database["Job_Info"].insert(
        {'_id':_id,
         'company_name':company_name,
         'department_name':department_name,
         'job':job,'about':about}
        )
    return "200"
    
### Client kayıt olduğunda iletişim bilgileri burada veritabanına aktarılır.
def insert_contact(objectid,email,number):
    current_database["Contact"].insert(
        {
            '_id':objectid,
            'email':email,
            'number':number
        }  
    )
    return "200"

### Client kayıt olduğunda durum bilgisi burada veritabanına aktarılır.
def insert_status(objectid):
    current_database["Status"].insert(
        {'_id':objectid,
         'status_name':"çevrimiçi",
         'status_color_code':'#008000'}
        )
    return "200"

### Client kayıt olduğunda sosyal medya bilgisi burada veritabanına aktarılır.
def insert_social(objectid):
    current_database["Social"].insert(
        {
            '_id':objectid,
            'social':[
                {
                    'name':"twitter",
                    'site_url':"",
                    'image_url':""
                },
                {
                    'name':"linkedin",
                    "site_url":"",
                    'image_url':""
                }
            ]
        }
    )
    


### UPDATE REQUEST

### Kullanıcı durumunu güncellemek istediği zaman bu fonksyion çalışır.
def update_status(objectid,data):
    current_database["Status"].update({'_id':ObjectId(objectid)},{'$set':
        {'status_name':data["status_name"],
         'status_color_code':data["status_color_code"]
         }})
    return  "200"

### Kullanıcı profilini güncellemek istediği zaman bu fonksiyon çalışır.
def update_profile(objectid,data):
    current_database["Profile"].update({'_id':ObjectId(objectid)},{'$set':
        {'username':data["username"],
         'password':data["password"],
         'name_surname':data["name_surname"],
         'profile_picture_url':data["profile_picture_url"],
         }})
    current_database["Contact"].update({'_id':ObjectId(objectid)},{'$set':
        {'email':data["contact"][0]['email'],
         'number':data["contact"][0]['number']
         }})
    return  "200"

### Kullanıcı iş bilgilerini güncellemek istediği zaman bu fonksiyon çalışır.
def update_job_info(objectid,data):
    current_database["Job_Info"].update({'_id':ObjectId(objectid)},{'$set':
        {'company_name':data["company_name"],
         'department_name':data["department_name"],
         'job':data["job"],
         'about':data["about"]
         }})
    return "200"

### Kullanıcı sosyal medya bilgilerini güncellemek istediği zaman bu fonksiyon çalışır.
def update_social(objectid,data):
    current_database["Social"].update({'_id':ObjectId(objectid),'social.name':'twitter'},{
        '$set':{
            'social.$.site_url':data['social'][0]['site_url'],
            'social.$.image_url':data['social'][0]['image_url']
        }
    })
    current_database["Social"].update({'_id':ObjectId(objectid),'social.name':'linkedin'},{
        '$set':{
            'social.$.site_url':data['social'][1]['site_url'],
            'social.$.image_url':data['social'][1]['image_url']
        }
    })
    return "200"

### QUERY REQUEST
### Uygulamanın ana sayfasında aynı departmandaki kişilerin profil,durum,iletişim bilgileri,sosyal medyalarını döndürür.

def query_by_department_name(department_name):
    cursor = current_database["Job_Info"].aggregate([{'$match':{'department_name':department_name}},
        {'$lookup':{'from':"Profile",'localField':"_id",'foreignField':"_id",'as':"profile"}},
        {'$unwind':'$profile'},
        {'$lookup':{'from':"Contact",'localField':"_id",'foreignField':"_id",'as':"contact"}},
        {'$unwind':'$contact'},
        {'$lookup':{'from':"Status",'localField':"_id",'foreignField':"_id",'as':"status"}},
        {'$unwind':'$status'}
        ])
    result = []
    for document in cursor:
        result.append(document)
    return Response(JSONEncoder().encode(result),mimetype='application/json')   


