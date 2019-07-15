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
group_post = ""

@app.route("/")
@app.route("/login", methods=['GET','POST'])
def login():
    return render_template('Login.html')

@app.route("/main", methods=['GET', 'POST'])
def main():
    return render_template('Main.html')

@app.route("/getData", methods=['GET', 'POST'])
def getData():
    selected_group_id = request.form.get('selected_group_id', 0)
    group_post = db.child("posts").child("selected_group_id").get()
    return json.dumps('traveldiary')

@app.route("/getDatas", methods=['GET', 'POST'])
def getDatas():
    group_post = db.child("posts").get()
    return redirect(url_for("traveldiary"))

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    return render_template('Login.html')

@app.route("/traveldiary", methods=['GET', 'POST'])
def traveldiary(posts=None):
    posts = group_post
    return render_template('TravelDiary.html', post=posts)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    return render_template('Upload.html')

@app.route('/citylist', methods=['GET', 'POST'])
def citylist():
    city_list = db.child("citylist").get()
    return json.dumps(city_list.val())

@app.route("/post", methods=['GET', 'POST'])
def post():
    return render_template('Post.html')

#
# def traveldiary(id=None):
#     city_name = request.form.get('selected_group_id', 0)
#     return render_template('TravelDiary.html', city_name)
#     return redirect(url_for('main'))
    # city_post = db.child("diary").get()
    # to = todo.val()
	# return


if __name__ == '__main__':
  app.run(host="0.0.0.0",debug=True)
# -> main.html
