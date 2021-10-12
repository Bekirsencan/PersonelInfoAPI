from users import Users
from encoder import *
from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Response

client = MongoClient("mongodb+srv://bekirsencan:Turtoise@cluster0.vfdtl.mongodb.net/PersonelAPP?retryWrites=true&w=majority")### MongoDB  bağlantısı oluşturdum.
current_database = client['PersonelAPP']


class user_profile(Users):
    
    __instance__ = None
    
    def __init__(self):
        if user_profile.__instance__ is None:
            user_profile.__instance__ = self
        else:
            raise Exception("Instance Active.Method Get Instance")
    
    def getInstance():
        if not user_profile.__instance__:
            user_profile()
        return user_profile.__instance__
    
    def get_profile(self,objectid):
        cursor = current_database["Profile"].aggregate([{'$match':{'_id':objectid}},
                                              {'$lookup':{'from':"Job_Info",'localField':"_id",'foreignField':"_id",'as':"job_info"}},
                                              {'$lookup':{'from':"Contact",'localField':"_id",'foreignField':"_id",'as':"contact"}},
                                              {'$lookup':{'from':"Status",'localField':"_id",'foreignField':"_id",'as':"status"}}])
        return Response(JSONEncoder().encode(list(cursor)),mimetype='application/json')
    
    def user_login(self,username,password):
        cursor = current_database["Profile"].find({'$and':[{'username':username},{'password':password}]},{'_id':1})
        return self.get_profile(list(cursor)[0]["_id"])


