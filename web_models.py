from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from web_init import db, login_manager, app

@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    google = db.Column(db.Boolean, default=False)
    verify = db.Column(db.Boolean, default=False)
    
    def get_token(self, expires_sec=1200): # 1200 seconds = 20 minutes
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return '<User %r>' % self.id


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    planname = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    courses = db.Column(db.String(100), nullable=False)
    AvgScore = db.Column(db.Float)
    EarlyTime = db.Column(db.String(20), nullable=False)
    LateTime = db.Column(db.String(20), nullable=False)
    planNum = db.Column(db.Integer, default=-1)
    
    def __repr__(self):
        return '<Plan %r>' % self.id