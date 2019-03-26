from flask import Flask,render_template,redirect,url_for,get_flashed_messages,request,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user
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

@login_manager.user_loader
def user_loader(user_id):
    return data_user.query.get(int(user_id))


class data_user(db.Model,UserMixin):
     id=db.Column(db.Integer,primary_key=True)
     user_name=db.Column(db.String(20),unique=True,nullable=False)
     email = db.Column(db.String(120),unique=True,nullable=False)
     password=db.Column(db.String(60),nullable=False)

     def __repr__(self):
          return f"data_user('{self.user_name}','{self.email}')"

class reports(db.Model,UserMixin):
     id=db.Column(db.Integer,primary_key=True)
     message=db.Column(db.String(100),nullable=False)
     def __repr__(self):
          return f"report('{self.message}')"

@app.route("/")
def user():
   return render_template('home.html')

@app.route("/logged/<username>")
def sessions(username):
    return render_template('session.html',username=username)


@app.route("/logged/server")
def admin():
    return render_template('admin.html',reports=reports)


def messageReceived(methods=['GET', 'POST']):
    print('successfully received message!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


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
                return redirect(url_for('admin'))
            elif(u2.email==mail):
                if(u2.password==pw):
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
         db.session.commit()         
         return redirect(url_for('success',username=username)) 

   return render_template('signup.html',form=form)



if __name__=="__main__":
   app.run(debug=True)
