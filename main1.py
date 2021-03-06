from flask import Flask,render_template,redirect,url_for,get_flashed_messages,request,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError,InvalidRequestError
from flask_login import LoginManager,UserMixin,login_required,login_user,logout_user
from flask_socketio import SocketIO
from form import Regis_form,login_form
from datetime import datetime
from flask_mail import Mail,Message



app=Flask(__name__)



socketio = SocketIO(app)

app.config['SECRET_KEY']="b0fc8e666068108a7254175f001919e1"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data_new.db'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']="**********@gmail.com"
app.config['MAIL_PASSWORD']="*********"
app.config['MAIL_USE_TSL']=False
app.config['MAIL_USE_SSL']=True

mail=Mail(app)

db=SQLAlchemy(app)
login=LoginManager(app)
     
class database(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     user_name=db.Column(db.String(20),unique=True,nullable=False)
     email = db.Column(db.String(120),unique=True,nullable=False)
     password=db.Column(db.String(60),nullable=False)

     def __repr__(self):
          return f"database('{self.user_name}','{self.email}')"

class user_code(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     user_name=db.Column(db.String(20),nullable=False)
     message=db.Column(db.String(100),nullable=False)
     date=db.Column(db.String,nullable=False)
     def __repr__(self):
          return f"user_code('{self.user_name}','{self.message}','{self.date}')"


class log2(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     user_name=db.Column(db.String(20),unique=True,nullable=False)
     def __repr__(self):
          return f"log2('{self.user_name}')"


@login.user_loader
def load_user(id):
    return log2.query.get(int(id))



@app.route("/")
def user():
   return render_template('home.html')


@app.route("/logged/<username>")
#@login_required
def sessions(username):
      form=login_form()

      u2=log2.query.filter_by(user_name=username).first()
      print(u2)
      if(u2 is None):
           return redirect(url_for('login'))
      
      elif(username=='zuerst'):     
          return render_template('admin.html',username=username,user_code=user_code,log2=log2) 
          return render_template('report.html',username=username,user_code=user_code) 
      else:
        return render_template('session.html',username=username,log2=log2)
        return render_template('report.html',username=username,user_code=user_code)   

@app.route("/logged/server")
def admin():
    return render_template('admin.html')

def messageReceived(methods=['GET', 'POST']):
    print('successfully received message!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    un=json.get('user_name','default')
    print(un)
    print(json.get('message','default'))
    mess=json.get('message','default')
    now=datetime.now()
    print(now)
    dt=now.strftime("%d/%m/%Y  %H:%M:%S")
    print(dt)
    socketio.emit('my response', json, callback=messageReceived)
    if(un!='default'):
        if(mess!='default'):
            us=user_code(user_name=un,message=mess,date=dt)
            db.session.add(us)
            db.session.commit()    
      
@app.route("/report")
def report():
    return render_template('report.html',user_code=user_code)


@app.route("/login",methods=['GET','POST'])
def login():
   form=login_form()
   if form.validate_on_submit():
      mail=request.form.get("email")
      pw=request.form.get("password")
      user=request.form.get("username")
     
      u2=database.query.filter_by(user_name=user).first()
      print(database.query.all())
      if(u2 is None):
          print(u2)
          return render_template('login.html',form=form)      
      
      elif(u2.user_name=='zuerst'):
          if(u2.password=='zuerst123'):
                   u=log2(user_name=u2.user_name)
                   db.session.add(u)
                   db.session.commit()
                   print(log2.query.all())
                   return redirect(url_for('sessions',username=user))
      
      elif(u2.email==mail):
            if(u2.password==pw):
                   u=log2(user_name=u2.user_name)
                   try:
                       db.session.add(u)
                       db.session.commit()
                       print(log2.query.all())
                       return redirect(url_for('sessions',username=user))
                   
                   except (InvalidRequestError,IntegrityError):
                       return redirect(url_for('sessions',username=user)) 

      error='invalid login'
      return render_template('login.html',form=form,error=error)   
   return render_template('login.html',form=form)



@app.route("/logout/<username>")
def logout(username):
      m=log2.query.filter_by(user_name=username).first()
      db.session.delete(m)
      db.session.commit()
      print(m)
      print(log2.query.all())
      return redirect(url_for('login'))


@app.route("/verification/<email>")
def verification(email):
      msg = Message('Hello', sender = '***********@gmail.com', recipients = [email])
      msg.body='hey there... please click on the link below to verify your mail \n http://127.0.0.1:5000/success/email'
      mail.send(msg)
      return "a veification mail is sent to %s ... please verify your account" %email


@app.route("/success/<email>")
def success(email):
   
   return render_template('success.html',email=email)

@app.route("/signup",methods=['GET','POST'])
def signup():
   form=Regis_form()
   if form.validate_on_submit():
         username=request.form.get("username")
         e2=request.form.get("email")
         pwd=request.form.get("password")
         user=database(user_name=username,email=e2,password=pwd)
         db.session.add(user)
         try:
             db.session.commit()
         except (InvalidRequestError,IntegrityError):
           error='that username/email already exists'
           db.session.rollback()
           return render_template('signup.html',form=form,error=error)        
                      
         return redirect(url_for('verification',email=e2))
         return redirect(url_for('success',username=username)) 

   return render_template('signup.html',form=form)



if __name__=="__main__": 
      app.run(debug=True)
