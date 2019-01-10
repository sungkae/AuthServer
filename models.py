import datetime
import jwt
import userAPIServer

def encode_auth_token(self, user_id):
    try:
        payload={
            'exp': datetime.datetime.utcnow()+datetime.timedelta(days=0,seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            userAPIServer.app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e :
        return e