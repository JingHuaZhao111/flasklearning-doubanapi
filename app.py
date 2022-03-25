from flask import Flask,render_template,flash,request,redirect,jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
import pymysql
import re
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
    url = "https://api.wmdb.tv/api/v1/top?type=Imdb&skip=0&limit=100&lang=Cn"
    response = requests.get(url).json()
    films_list = []
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
        films_list.append(film)
    # 把所有数据提交给用户会话
    db.session.add_all(films_list)
    # 提交会话
    db.session.commit()
    return redirect('http://127.0.0.1:5000/')

'''
def paqu():
    #先清空数据库中的表再创建表
    db.drop_all()
    db.create_all()
    url="https://api.wmdb.tv/api/v1/top?type=Imdb&skip=0&limit=100&lang=Cn"
    response = requests.get(url)
    #将获取的转化为列表
    data=re.compile(r'"data":.*?dateReleased".*?}')
    #获取一部电影所有信息
    all_data=re.findall(data,response.text)
    #将列表每部电影的数据构造一个数据库对象
    films_list=[]
    for i in all_data:
        #利用正则表达式获得所有电影信息创建电影对象
        doubanid=re.findall(r'"doubanId":"(.*?)"',i)
        name = re.findall(r'"name":"(.*?)"',i)
        genre = re.findall(r'"genre":"(.*?)"',i)
        description = re.findall(r'"description":"(.*?)"',i)
        language = re.findall(r'"language":"(.*?)"',i)
        country = re.findall(r'"country":"(.*?)"',i)
        alias = re.findall(r'"alias":"(.*?)"',i)
        originalName = re.findall(r'"originalName":"(.*?)"',i)
        doubanRating = re.findall(r'"doubanRating":"(.*?)"',i)
        dateReleased = re.findall(r'"dateReleased":"(.*?)"',i)
        doubanid=int(doubanid[0])
        name=name[0]
        language=language[0]
        country=country[0]
        originalName=originalName[0]
        if len(doubanRating)!=0:
            doubanRating=float(doubanRating[0])
        else:
            doubanRating=""
        if len(dateReleased)!=0:
            dateReleased=dateReleased[0]
        else:
            dateReleased=""
        if len(genre)!=0:
            genre=genre[0]
        else:
            genre=""
        if len(description)!=0:
            description=description[0]
        else:
            description=""
        if len(alias)!=0:
            alias=alias[0]
        else:
            alias=""
        film=Film(Doubanid=doubanid,Name=name,Genre=genre,Description=description,Language=language,Country=country,Alias=alias,OriginalName=originalName,DoubanRating=doubanRating,DateReleased=dateReleased)
        films_list.append(film)
    # 把所有数据提交给用户会话
    db.session.add_all(films_list)
    # 提交会话
    db.session.commit()
    #重定向，回到原始页面
    return redirect('http://127.0.0.1:5000/')
'''

'''
清空数据库
'''
@app.route('/clear',methods=['GET'])
def clear():
    db.drop_all()
    #重定向
    return redirect('http://127.0.0.1:5000/')

'''
网页操作：表单类
'''
class FilmForm(FlaskForm):
    film_id=StringField('请输入豆瓣id',validators=[DataRequired()])
    check=SubmitField('按豆瓣id查找条目')

'''
通过id查找电影函数
'''
def search_film(film_id):
    try:
        film = Film.query.get(film_id)
        if film:
            try:
                #显示信息
                flash('电影条目：'+str(film.Doubanid))
                flash('中文名：' + film.name)
                flash('影片类型：'+film.Genre)
                flash('简介：'+film.Description)
                flash('语言：'+film.Language)
                flash('制片国家：'+film.Country)
                flash('别名：'+film.Alias)
                flash('官方名字：'+film.OriginalName)
                flash('豆瓣评分：'+str(film.DoubanRating))
                flash('上映时间：'+film.DateReleased)
            except Exception as e:
                print(e)
                flash('查询错误')
        else:
            flash('此豆瓣id不存在')
    except Exception as e:
        flash('该表不存在或者数据库不存在，请爬取')

'''
显示所有数据网页
'''
@app.route('/show',methods=['GET','POST'])
def show():
    try:
        films = Film.query.all()
        return render_template('show.html', films=films)
    except Exception as e:
        return '数据库中无表，请爬取数据'

'''
打开后的显示界面
'''
@app.route('/',methods=['GET','POST'])
def origin():
    film_form = FilmForm()
    if film_form.validate_on_submit():
        # 获取数据
        id = int(film_form.film_id.data)
        #调用查找函数
        search_film(id)
    return render_template('origin.html', form=film_form)

if __name__ == '__main__':
    app.run(debug=True)
