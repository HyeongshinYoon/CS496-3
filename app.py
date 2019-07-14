import pyrebase
from flask import *

config = {
    "apiKey": "AIzaSyDmn0dJl4lvTASIPtPD5vfHIoG6IIWg5dc",
    "authDomain": "travel-b97bd.firebaseapp.com",
    "databaseURL": "https://travel-b97bd.firebaseio.com",
    "projectId": "travel-b97bd",
    "storageBucket": "travel-b97bd.appspot.com",
    "messagingSenderId": "850989183342",
    "appId": "1:850989183342:web:6eb717f390c612c8"
}

app = Flask(__name__)
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()

@app.route("/")
@app.route("/Login", methods=['GET', 'POST'])
def Login():
    unsuccessful = 'Please check your credentials'
    successful = 'Login successful'
    if request.method == 'POST':
        email = request.form['text']
        password = request.form['password']
        try:
            auth.sign_in_with_email_and_password(email, password)
            return render_template('Main.html', s=successful)
        except:
            return render_template('Login.html', us=unsuccessful)
    return render_template(
                'Login.html',
                title="Travel",
            )

@app.route("/Main", methods=['GET', 'POST'])
# @login_required
def Main():
    id = request.form['id']
    return render_template('Main.html', id=id)


@app.route("/Logout", methods=['GET', 'POST'])
def logout(request):
    try:
        auth.signOut()
    except KeyError:
        pass
    return render_template('Login.html', us=unsuccessful)


if __name__ == '__main__':
  app.run(debug='true')
# -> main.html
