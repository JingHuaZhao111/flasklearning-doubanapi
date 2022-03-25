from flask import Flask,jsonify
import requests
from flask_sqlalchemy import SQLAlchemy

'''
连接数据库
'''
app = Flask(__name__)
DB_URI='mysql+pymysql://root:123456@127.0.0.1:3306/sqlFILM'
app.config['SQLALCHEMY_DATABASE_URI']=DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key='111'
db=SQLAlchemy(app)

'''
创建电影表
'''
class Film(db.Model):
    __tablename__ = 'films'
    #包含影片条目，中文名，影片类型，简介，语言，制片国家，别名,官方名字，豆瓣评分，上映时间
    Doubanid = db.Column(db.Integer, primary_key=True,unique=True)
    Name = db.Column(db.String(500))
    Genre=db.Column(db.String(500))
    Description=db.Column(db.String(500))
    Language=db.Column(db.String(500))
    Country=db.Column(db.String(500))
    Alias=db.Column(db.String(500))
    OriginalName=db.Column(db.String(500))
    DoubanRating=db.Column(db.Float)
    DateReleased=db.Column(db.String(500))
'''
爬取网页并传到数据库函数函数
'''
@app.route('/paqu',methods=['GET'])
def paqu():
    # 先清空数据库中的表再创建表
    db.drop_all()
    db.create_all()
    #获取所有数据
    url = "https://api.wmdb.tv/api/v1/top?type=Imdb&skip=0&limit=100&lang=Cn"
    response = requests.get(url).json()
    films_list = []
    json_list=[]
    #处理数据将每个电影数据创建电影对象
    for i in response:
        doubanid =int(i.get("doubanId"))
        data = (i.get("data"))
        name=data[0].get("name")
        genre = data[0].get("genre")
        description = data[0].get("description")
        language = data[0].get("language")
        country = data[0].get("country")
        alias = i.get("alias")
        originalName = i.get("originalName")
        doubanRating = float(i.get("doubanRating"))
        dateReleased = i.get("dateReleased")
        film = Film(Doubanid=doubanid, Name=name, Genre=genre, Description=description, Language=language,
                    Country=country, Alias=alias, OriginalName=originalName, DoubanRating=doubanRating,
                    DateReleased=dateReleased)
        #用于返回前端的json
        film_dic={"doubanId" : doubanid, "name":name, "genre":genre, "description":description,"language":language,
                    "country":country, "alias":alias, "originalName":originalName, "doubanRating":doubanRating,
                    "dateReleased":dateReleased}
        json_list.append({"data":film_dic})
        films_list.append(film)
    # 把所有数据提交给用户会话
    db.session.add_all(films_list)
    # 提交会话
    db.session.commit()
    #检测电影数量
    print(len(json_list))
    return jsonify(json_list)


'''
清空数据库
'''
@app.route('/clear',methods=['GET'])
def clear():
    db.drop_all()
    return jsonify({"data":'已清空数据库'})


'''
通过id查找电影函数
'''
def search_film(film_id):
    dic={}
    try:
        film = Film.query.get(film_id)
        if film:
            try:
                #显示信息
                dic.update({"电影条目：" : str(film.Doubanid), "中文名":film.name, "影片类型：":film.Genre, "简介":film.Description, "语言：":film.Language,
                    "制片国家：":film.Country, "别名：":film.Alias, "官方名字：":film.OriginalName, "豆瓣评分：":str(film.DoubanRating),
                    "上映时间：":film.DateReleased})
            #不清楚何时产生这种情况
            except Exception as e:
                dic.update({"data":'查询错误，错误代码:%s'%e})
        else:
            dic.update({"data": '此豆瓣id不存在'})
    except Exception as e:
        dic.update({"data":'该表不存在或者数据库不存在，请爬取'})
    return dic

@app.route('/<id>',methods=['GET'])
def origin(id):
    data=search_film(id)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)