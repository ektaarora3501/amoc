from flask import Flask,render_template,redirect,url_for,get_flashed_messages,request,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError,InvalidRequestError
from flask_login import LoginManager,UserMixin,login_user,login_required
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from form import Regis_form,login_form
bcrypt=Bcrypt()

app=Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY']="b0fc8e666068108a7254175f001919e1"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data_new.db'

db=SQLAlchemy(app)
login_manager=LoginManager(app)
     
class data_user(db.Model,UserMixin):
     id=db.Column(db.Integer,primary_key=True)
     user_name=db.Column(db.String(20),unique=True,nullable=False)
     email = db.Column(db.String(120),unique=True,nullable=False)
     password=db.Column(db.String(60),nullable=False)

     def __repr__(self):
          return f"data_user('{self.user_name}','{self.email}')"

class ucode(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     user_name=db.Column(db.String(20),nullable=False)
     message=db.Column(db.String(100),nullable=False)
     def __repr__(self):
          return f"ucode('{self.user_name}',{self.message}')"


class log(db.Model):
     id=db.Column(db.Integer,primary_key=True)
     user_name=db.Column(db.String(20),unique=True,nullable=False)
     def __repr__(self):
          return f"log('{self.user_name}')"



@app.route("/")
def user():
   return render_template('home.html')


@app.route("/logged/<username>")
#@login_required
def sessions(username):
      form=login_form()
      i=1
      u2=log.query.filter_by(id=i).first()
      while(1):
         u2=log.query.filter_by(id=i).first()
         if(u2 is None):
            break

         elif(username==u2.user_name):     
             return render_template('session.html',username=username) 
         
         else:
           i=i+1
     
      error='you are not logged in '     
      return render_template('login.html',form=form,error=error)   


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
    socketio.emit('my response', json, callback=messageReceived)
    if(un!='default'):
        if(mess!='default'):
            us=ucode(user_name=un,message=mess)
            db.session.add(us)
            db.session.commit()    
    
    


@app.route("/login",methods=['GET','POST'])
def login():
   form=login_form()
   if form.validate_on_submit():
      mail=request.form.get("email")
      pw=request.form.get("password")
      user=request.form.get("username")
      i=1
      u2=data_user.query.filter_by(id=i).first()
      while(1):
         u2=data_user.query.filter_by(id=i).first()
         if(u2 is None):
            break
         else:
            if(u2.user_name=='server'):
                 if(u2.password=='zuerst123'):
                     return redirect(url_for('admin'))
            elif(u2.email==mail):
                if(u2.password==pw):
                   u=log(user_name=u2.user_name)
                   db.session.add(u)
                   db.session.commit()
                   return redirect(url_for('sessions',username=user))
            
         i=i+1
      error='invalid login'
      return render_template('login.html',form=form,error=error)   
   return render_template('login.html',form=form)

@app.route("/success/<username>")
def success(username):
   
   return render_template('success.html',username=username)

@app.route("/signup",methods=['GET','POST'])
def signup():
   form=Regis_form()
   if form.validate_on_submit():
         username=request.form.get("username")
         e2=request.form.get("email")
         pwd=request.form.get("password")
         user=data_user(user_name=username,email=e2,password=pwd)
         db.session.add(user)
         try:
             db.session.commit()
         except (InvalidRequestError,IntegrityError):
           error='that username/email already exists'
           db.session.rollback()
           return render_template('signup.html',form=form,error=error)        
                      
         return redirect(url_for('success',username=username)) 

   return render_template('signup.html',form=form)



if __name__=="__main__":
   app.run(debug=True)
