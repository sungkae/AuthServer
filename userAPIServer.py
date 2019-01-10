from flask import Flask, render_template, session
from flask_restful import Api, Resource, reqparse
from flaskext.mysql import MySQL
from flask_api import status
import hashlib
import os
import models

app = Flask(__name__)
api = Api(app)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '505050'
app.config['MYSQL_DATABASE_DB'] = 'authtest'
mysql = MySQL(app)
parser = reqparse.RequestParser()

def sha256(text, salt):
    hash = hashlib.sha256()
    newtext = text+salt
    print(newtext)
    hash.update((newtext).encode())
    result = hash.hexdigest()
    return result

@app.route('/')
def index():
    print(session.get('logged_in'))
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return "Hello Boss"

@app.route('/register')
def register():
    return render_template('register.html')

class AuthServer(Resource):
    def post(self):
        # 1. index page에서 id, password 입력 받음.
        parser.add_argument('input_id', type=str)
        parser.add_argument('input_pwd', type=str)
        args = parser.parse_args()
        print(args['input_pwd'])
        cur = mysql.get_db().cursor()
        # 2. 입력받은 id로 데이터베이스 조회.
        cur.execute('''SELECT * FROM user WHERE user_id = %s''', (args['input_id']))

        # 3. 무조건 하나만 받을 테니 fetch one
        #   all로 받을 땐 조건문
        result = cur.fetchone()

        # for debug (id, user_id, user_pwd, user_salt ) , length
        print(result)
        print(len(result))
        hashed = sha256(args['input_pwd'], result[3])
        print("hashed = "+ hashed)
        print(result[2])
        if result[2] == hashed:
            print("welcome!!!")
            session['logged_in'] = True
            print(session['logged_in'])
        else:
            print("?????????")
        return {
            'status': 200,
            'token': 'yes'
        }, status.HTTP_202_ACCEPTED

class UserAPI(Resource):
    def get(self, id):
        return {'user_id': id}

    def put(self, id):
        # Database update
        pass

    def delete(self, id):
        # Database Delete
        pass

    def post(self):
        # Database Insert
        parser.add_argument('user_id', type=str)
        parser.add_argument('user_pwd', type=str)
        parser.add_argument('user_salt', type=str)
        #for debug
        parser.add_argument('user_pww', type=str)
        args = parser.parse_args()
        print("hashed password = "+args['user_pwd'])
        print(type(args['user_pwd']))
        print("salt = "+args['user_salt'])
        print("password = "+ args['user_pww'])
        cur = mysql.get_db().cursor()
        # 중복확인
        cur.execute('''SELECT * FROM user WHERE user_id = %s''', (args['user_id']))
        returnvals = cur.fetchall()
        if len(returnvals) == 0:
            cur.execute('''INSERT INTO user (user_id, user_pwd, user_salt) VALUES(%s, %s, %s)''',
                        (args['user_id'], args['user_pwd'], args['user_salt']))
            mysql.get_db().commit()
            return {
                'status': '200',
                'user_id': args['user_id'],
                'user_pwd': args['user_pwd'],
                'user_salt': args['user_salt']
            }, status.HTTP_200_OK

        else:
            print("fail [ "+args['user_id']+", "+args['user_pwd']+", "+args['user_salt']+" ]")
            return {
                'status': '404',
                'message': 'already exists'
            }, status.HTTP_404_NOT_FOUND

api.add_resource(UserAPI, '/register', '/register/<int:id>', endpoint='/')
api.add_resource(AuthServer, '/login', endpoint='/login')

if __name__ == '__main__':
    app.secret_key=os.urandom(12)
    app.run('127.0.0.1',port=5000,threaded=True)