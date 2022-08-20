# Aplicación
from flask import Flask, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_security import Security, current_user
from utils.db import db
from utils.filters import fecha, hora
from flask_migrate import Migrate


from models.gymModels import Users, Stats, user_datastore, Roles
from routes.gym import gym

# Configurar web-app
app = Flask(__name__)
app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
app.config['SECRET_KEY'] = 'ha94LHj6S-Cat3Q'
app.config['SECURITY_PASSWORD_SALT'] = 'h(Xcbix39gtrQII'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.filters["hora"] = hora
app.jinja_env.filters["fecha"] = fecha

# SQL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:LM46780396@localhost/catelottidb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cjmkxblioaatzt:b60269893ff19ac01204bc6889a75679edfa6bd4e78994575b91fa5dffbb4487@ec2-34-227-135-211.compute-1.amazonaws.com:5432/d6rv3rv72nh9gr'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
    db.session.commit()

# Admin
class AdminView(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin') or current_user.has_role('Profesor')
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect("/")

admin = Admin(app)
admin.add_view(AdminView(Users, db.session))
admin.add_view(AdminView(Stats, db.session))
admin.add_view(AdminView(Roles, db.session))

# Login
login = LoginManager()
login.init_app(app)

@login.user_loader
def load_user(user_id):
    user = db.session.query(Users).get(int(user_id))
    db.session.commit()
    return user

# Security
app.config["SECURITY_LOGIN_URL"] = "/securitylogin"
security = Security(app, user_datastore)

# Migrate
migrate = Migrate(app, db)

# Configurar mail
MAIL_SERVER = 'TODO'
MAIL_USERNAME = 'TODO'
MAIL_PASSWORD = 'TODO'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False

# Cargar el blueprint
app.register_blueprint(gym)

