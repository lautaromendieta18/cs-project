#  Rutas de mi aplicación Web.
import os
from flask import Blueprint, render_template, request, redirect, send_from_directory
from flask_security import roles_accepted
from flask_login import login_required, logout_user, current_user
from flask_security.utils import login_user
from models.gymModels import Users, Stats, Schedule, Frases, user_datastore
from werkzeug.security import check_password_hash, generate_password_hash
from utils.db import db
from datetime import date, datetime, timedelta, time
from pytz import timezone
from random import randrange

gym = Blueprint('gym', __name__)

HORARIOS_GYM = [time(9, 0), time(9, 30), time(10, 00), time(10, 30), time(11, 00), time(11, 30), time(12, 00), time(12, 30),
time(13, 00), time(13, 30), time(14, 00), time(14, 30), time(15, 00), time(15, 30), time(16, 00), time(16, 30), time(17, 00),
time(17, 30), time(18, 00), time(18, 30), time(19, 00), time(19, 30), time(20, 00), time(20, 30)]


@gym.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/perfil")
    else:
        return render_template("inicio.html")

@gym.route("/productos")
def productos():
    return render_template("productos.html")

@gym.route("/register", methods=['GET','POST'])
def register():
    logout_user()

    if request.method == 'POST':
        # Chequeos de seguridad


        if not request.form.get('username'):
            return render_template("error.html", num=400, error="DATO FALTANTE: Nombre.")
        if not request.form.get('email'):
            return render_template("error.html", num=400, error="DATO FALTANTE: Email.")
        if not request.form.get('number') or request.form.get('number') == 0:
            return render_template("error.html", num=400, error="DATO FALTANTE: Número de celular.")
        if not request.form.get("password"):
            return render_template("error.html", num=400, error="DATO FALTANTE: Contraseña.")
        if not request.form.get("confirmation"):
            return render_template("error.html", num=400, error="DATO FALTANTE: Confirmación")

        if request.form.get("plan") not in ["Estándar", "Personalizado", "Personal Trainer"]:
            return render_template("error.html", num=400, error="DATO INCORRECTO: Plan.")
        
        matches = db.session.query(Users).filter_by(username=request.form.get('username')).all()
        if len(matches) > 0:
            return render_template("error.html", num=400, error="Nombre de usuario en uso.")
        
        matchesmail = db.session.query(Users).filter_by(email=request.form.get('email')).all()
        if len(matchesmail) > 0:
            return render_template("error.html", num=400, error="El email ya está en uso.")

        if check_password_hash(generate_password_hash(request.form.get('password')), request.form.get('confirmation')) == False:
            return render_template("error.html", num=400, error="Las contraseñas no coinciden.")

        user_datastore.create_user(
                username = request.form.get('username'),
                email = request.form.get('email'),
                numero = "+54" + request.form.get('number'),
                hash = generate_password_hash(request.form.get('password')),
                fecha = datetime.now(timezone('America/Buenos_Aires')),
                plan = request.form.get("plan")
        )

        email = request.form.get('email')
        user = db.session.query(Users).filter_by(email=email).first()

        user_datastore.add_role_to_user(user, 'Visitante')

        db.session.commit()
        login_user(user, remember=True)

        return redirect('/')
    else:
        return render_template("register.html")

@gym.route("/login", methods=['GET','POST'])
def login():
    logout_user()

    if request.method == 'POST':

        if not request.form.get('email'):
            return render_template('error.html', num=400, error="DATO FALTANTE: E-mail.")
        if not request.form.get('password'):
            return render_template('error.html', num=400, error='DATO FALTANTE: Contraseña.')
        
        if not db.session.query(Users).filter_by(email=request.form.get('email')).first():
            return render_template("error.html", num=400, error="No se ha encontrado ningún usuario con esos datos.")
        else:
            user = db.session.query(Users).filter_by(email=request.form.get('email')).first()
        
        db.session.commit()
        print(user)

        if not check_password_hash(user.hash, request.form.get('password')):
            return render_template("error.html", num=400, error="Contraseña Incorrecta")
        
        login_user(user, remember=True)

        return redirect('/')
    else:
        return render_template("login.html")


@gym.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/")

@gym.route("/estandar")
def estandar():
    return render_template("estandar.html")

@gym.route("/perfil")
@login_required
def profile():
    user = db.session.query(Users).filter_by(id=current_user.id).first_or_404()
    stats = db.session.query(Stats).filter_by(user_id=user.id).order_by(Stats.time.desc()).first()
    reservas = db.session.query(Schedule).filter_by(user_id=user.id).order_by(Schedule.dia.desc()).limit(2)
    frase = db.session.query(Frases).get(randrange(6))

    cuentareservas = db.session.query(Schedule).filter_by(user_id=user.id).order_by(Schedule.dia.asc()).all()
    cuentareservas = len(cuentareservas)
    db.session.commit()

    cuentadias = datetime.today() - user.fecha

    return render_template("profile.html", user=user, stats=stats, reservas=reservas, cuentadias=cuentadias, cuentareservas=cuentareservas, frase=frase)

@gym.route("/reservar", methods=["GET", "POST"])
@login_required
@roles_accepted('Admin', 'Profesor', 'Alumno')
def reservar():
    if request.method == "POST":
        id = current_user.id
        hoy = date.today()
        # hoy = hoy.strftime("%d-%m-%y")
        manana = date.today() + timedelta(days=1)
        # manana = manana.strftime("%d-%m-%y")

        # Chequeos de seguridad.
        consultahoy = db.session.query(Schedule).filter_by(user_id=id, dia=hoy).all()
        consultaman = db.session.query(Schedule).filter_by(user_id=id, dia=manana).all()

        if request.form.get('dia') != None:
            input = request.form.get('dia')
            dia = datetime.strptime(input, '%Y-%m-%d')
            dia = dia.date()

            if dia.isoweekday() == 7 or dia.isoweekday() == 6:
                return render_template("error.html", num=400, error="Has introducido un día inválido.")

            print(type(dia))
            print(type(manana))

            if dia != hoy and dia != manana:
                print(dia)
                print(hoy)
                print(manana)
                return render_template("error.html", num=400, error="DATO INCORRECTO: Día.")

            if dia == hoy and len(consultahoy) > 0:
                return render_template("error.html", num=400, error="Ya has realizado una reserva para esta fecha, si quieres modificarla comunícate con un profesor.")
            if dia == manana and len(consultaman) > 0:
                return render_template("error.html", num=400, error="Ya has realizado una reserva para esta fecha, si quieres modificarla comunícate con un profesor.")
        else:
            return render_template("error.html", num=400, error="DATO FALTANTE: día de reserva.")
        
        
        if request.form.get('hora') != None:
            hora = datetime.strptime(request.form.get('hora'), '%H:%M:%S').time()
        
            if hora not in HORARIOS_GYM:
                return render_template("error.html", num=400, error="HORA INCORRECTA.")
        else:
            return render_template("error.html", num=400, error="DATO FALTANTE: hora de reserva.")

        if request.form.get('tipo') != None:
            tipo = request.form.get('tipo')

            if tipo != "Funcional" and tipo != "Musculación":
                return render_template("error.html", num=400, error="DATO INCORRECTO: tipo de reserva.")
        else:
            return render_template("error.html", num=400, error="DATO FALTANTE: tipo de reserva.")
            
        reserva = Schedule(id, dia, hora, tipo)
        db.session.add(reserva)
        db.session.commit()

        return redirect("/")
    else:
        hoy = date.today()
        diaHoy = hoy.isoweekday()
        print(diaHoy)

        manana = date.today() + timedelta(days=1)
        diaManana = manana.isoweekday()
        print(diaManana)

        return render_template("reservar.html", horario=HORARIOS_GYM, hoy=hoy, manana=manana, diaHoy=diaHoy, diaManana=diaManana)

@gym.route('/registros', methods=["GET", "POST"])
@login_required
@roles_accepted('Admin', 'Profesor', 'Alumno', 'Inactivo')
def registros():

    if request.method == "POST":
        return render_template("registros.html")
    else:
        user = db.session.query(Users).filter_by(id=current_user.id).first_or_404()
        frStat = db.session.query(Stats).filter_by(user_id=user.id).order_by(Stats.time.desc()).first()
        stats = db.session.query(Stats).filter_by(user_id=user.id).order_by(Stats.time.desc()).all()
            
        if frStat:
            fecha = frStat.time
            fecha = fecha.strftime("%d-%m-%y")
        else:
            fecha = date.today()
            fecha = fecha.strftime("%d-%m-%y")
            
        db.session.commit()
        return render_template("registros.html", user=user, stats=stats, frStat=frStat, fecha=fecha)

@gym.route("/add", methods=['POST'])
@login_required
def add():
    id = request.form.get("id")

    # Chequeos de seguridad
       
    if int(request.form["peso"]) != 0 and int(request.form["peso"]) > 0:
        peso = request.form["peso"]
        print(peso)
    else:
        return render_template("error.html", num=400, error="DATO INCORRECTO: peso.")
       
    if int(request.form["grasa1"]) != 0 and int(request.form["grasa1"]) > 0:
        porcentaje = request.form["grasa1"]
    else:
        return render_template("error.html", num=400, error="DATO INCORRECTO: grasa corporal.")
       
    if int(request.form["masa1"]) != 0 and int(request.form["masa1"]) > 0:
        masaMusc = request.form["masa1"]
    else:
        return render_template("error.html", num=400, error="DATO INCORRECTO: masa muscular.")
       
    if int(request.form["masa2"]) != 0 and int(request.form["masa2"]) > 0:
        masaOsea = request.form["masa2"]
    else:
        return render_template("error.html", num=400, error="DATO INCORRECTO: masa ósea.")
       
    if int(request.form["edad"]) != 0 and int(request.form["edad"]) > 0:
        edad = request.form["edad"]
    else:
        return render_template("error.html", num=400, error="DATO INCORRECTO: edad biológica.")
       
    if int(request.form["grasa2"]) != 0 and int(request.form["grasa2"]) > 0:
        grasa = request.form["grasa2"]
    else:
        return render_template("error.html", num=400, error="DATO INCORRECTO: grasa visceral.")
        
    time = datetime.now(timezone('America/Buenos_Aires'))
 

    stat = Stats(id, peso, porcentaje, masaMusc, masaOsea, edad, grasa, time)
    db.session.add(stat)
    db.session.commit()

    return redirect("/profesor")

@gym.route("/profesor/delete/registro", methods=["POST"])
@roles_accepted('Admin', 'Profesor')
def delete():
    statid = request.form["statid"]

    stat = Stats.query.filter_by(id=statid).first()
    
    db.session.delete(stat)
    db.session.commit()

    return redirect("/profesor")

@gym.route("/turnos")
@login_required
@roles_accepted('Admin', 'Profesor')
def turnos():
    hoy = date.today()
    
    manana = date.today() + timedelta(days=1)
    
    user = db.session.query(Users).all()
    planhoy = db.session.query(Schedule)\
        .filter_by(dia=hoy)\
        .order_by(Schedule.hora.asc())\
        .join(Users, Schedule.user_id==Users.id)\
        .add_columns(Schedule.id, Schedule.user_id, Users.username, Schedule.dia, Schedule.hora, Schedule.tipo)\
        .all()

    planmanana = db.session.query(Schedule)\
        .filter_by(dia=manana)\
        .order_by(Schedule.hora.asc())\
        .join(Users, Schedule.user_id==Users.id)\
        .add_columns(Schedule.id, Schedule.user_id, Users.username, Schedule.dia, Schedule.hora, Schedule.tipo)\
        .all()

    db.session.commit()
        
    return render_template("turnos.html", hoy=planhoy, manana=planmanana, user=user, fechahoy=hoy, fechamanana=manana, horario=HORARIOS_GYM)

@gym.route("/turnos/edit", methods=["POST"])
def editar_turno():
    id = request.form.get("id")
    print(id)
    hora = request.form.get("hora")

    reserva = db.session.query(Schedule).get(id)
    reserva.hora = hora

    db.session.commit()

    return redirect("/turnos")


@gym.route("/profesor", methods=["GET", "POST"])
@roles_accepted('Admin', 'Profesor')
def profesor():
    if request.method == "POST":
        return render_template('panel.html')
    else:
        users = db.session.query(Users).all()
        stats = db.session.query(Stats).all()
        
        db.session.commit()
        return render_template('panel.html', users=users, stats=stats)

@gym.route("/profesor/delete", methods=["POST"])
@login_required
@roles_accepted('Admin', 'Profesor')
def delete_profesor():
    if current_user.has_role('admin') or current_user.has_role('Profesor'):
        user = db.session.query(Users).filter_by(id=request.form["id"]).first()
        stats = db.session.query(Stats).filter_by(user_id=user.id).all()
        reservas = db.session.query(Schedule).filter_by(user_id=user.id).all()

        for stat in stats:
            db.session.delete(stat)
        for reserva in reservas:
            db.session.delete(reserva)
    
        db.session.delete(user)
    

        db.session.commit()


        return redirect("/profesor")
    else:
        return redirect("/")

@gym.route("/profesor/verificar", methods=["POST"])
@login_required
@roles_accepted('Admin', 'Profesor')
def verificar_usuario():
    id = request.form.get("id")
    user = db.session.query(Users).get(id)
    user.roles.remove(user.roles[0])

    user_datastore.add_role_to_user(user, 'Alumno')

    db.session.commit()


    return redirect("/profesor")

@gym.route("/profesor/edit", methods=["POST"])
@login_required
@roles_accepted('Admin', 'Profesor')
def editar():
    user = db.session.query(Users).get(request.form.get("id"))
    user.plan = request.form.get("nuevoPlan")

    db.session.commit()
    return redirect("/profesor")

@gym.route("/profesor/search")
@login_required
@roles_accepted('Admin', 'Profesor')
def search():
    id = request.args.get("id")
    email = request.args.get("email")
    plan = request.args.get("plan")


    if id and plan:
        user = db.session.query(Users).filter_by(id=id, plan=plan).all()
    elif email and plan:
        user = db.session.query(Users).filter_by(email=email, plan=plan).all()
    elif id:
        user = db.session.query(Users).filter_by(id=id).all()
    elif email:
        user = db.session.query(Users).filter_by(email=email).all()
    elif plan:
        user = db.session.query(Users).filter_by(plan=plan).all()
    
    stats = db.session.query(Stats).all()

    db.session.commit()

    return render_template("search.html", users=user, stats=stats)

@gym.route("/profesor/bajar", methods=["POST"])
@login_required
@roles_accepted('Admin', 'Profesor')
def bajar_usuario():
    id = request.form.get("id")
    user = db.session.query(Users).get(id)
    user.roles.remove(user.roles[0])

    user_datastore.add_role_to_user(user, 'Inactivo')

    db.session.commit()


    return redirect("/profesor")