import pyrebase
from flask import *
from werkzeug.utils import secure_filename
from PIL import Image


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
storage = firebase.storage()
group_post = {}
city_titles = ""
last_post_id = 0

@app.route("/")
@app.route("/login", methods=['GET','POST'])
def login():
    return render_template('Login.html')

@app.route("/main", methods=['GET', 'POST'])
def main():
    global last_post_id;
    last_post_id = db.child("Last_post_id").get()
    if last_post_id == None:
        last_post_id = 0
    return render_template('Main.html')

@app.route("/citytitles", methods=['GET', 'POST'])
def citytitles():
    city_titles = db.child("posts").get()
    return json.dumps(city_titles)

@app.route("/setData", methods=['GET', 'POST'])
def setData():
    return json.dumps('traveldiary?cityId=')

@app.route("/getData/<name>", methods=['GET', 'POST'])
def getData(name):
    selected_group_id = name
    group_post_id = db.child("tag").child(selected_group_id).get()
    global group_post
    group_post = {}
    if group_post_id.each() == None:
        return json.dumps('')
    else:
        for id in group_post_id.each():
            post = db.child("posts").child(id.val()).get()
            group_post[id.val()]=(post.val())

    return json.dumps(group_post)

@app.route("/getDataId/<id>", methods=['GET', 'POST'])
def getDataId(id):
    post = db.child("posts").child(id).get().val()
    return json.dumps(post)

@app.route("/getDatas", methods=['GET', 'POST'])
def getDatas():
    group_post = db.child("posts").get().val()
    return json.dumps(group_post)

@app.route("/getPhoto/<filename>", methods=['GET', 'POST'])
def getPhoto(filename=None):
    text = filename.strip('"')
    photo = storage.child(text).get_url("hello.png")
    return photo

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    return render_template('Login.html')

@app.route("/traveldiary", methods=['GET', 'POST'])
def traveldiary(posts=None):
    return render_template('TravelDiary.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        global last_post_id
        last_post_id = db.child("last_post_id").get().val()
        if last_post_id == None:
            last_post_id = 0

        title = request.form['title']
        subtitle = request.form['subtitle']
        tag = request.form.getlist('tag')
        photos = request.files.getlist('photos')
        files = []

        for photo in photos:
            storage.child(photo.filename).put(photo)
            files.append(photo.filename)

        data = [{"title":title,"subtitle":subtitle,"tag":tag,"files":files}]
        db.child('posts').child(last_post_id).push(data)

        for tag_id in tag:
            db.child("tag").child(tag_id).push(last_post_id)
        last_post_id = last_post_id + 1
        db.child("last_post_id").set(last_post_id)
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
