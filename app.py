from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template, flash
from lib.get_overall_grades import populate
from werkzeug.utils import secure_filename
import json, os

UPLOAD_FOLDER = './static/'
ALLOWED_EXTENSIONS = set(['xlsx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Database stuff
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zyvadgtq:9hq4_JBlzW8vbAp7b1NFT-LOtcBzZ246@nutty-custard-apple.db.elephantsql.com:5432/zyvadgtq'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test@localhost/classTesting'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(10))
    grades = db.Column(db.JSON)

    def __init__(self, hash, grades):
        self.hash = hash
        self.grades = grades

    def __repr__(self):
        return '<Student {0}>'.format(self.hash)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile/<student_code>')
def profile(student_code):
    user = User.query.filter_by(hash = student_code).first()
    return render_template('profile.html', student_code=student_code, user=user)


@app.route('/post_student', methods = ['POST'])
def post_student():
    student_code = request.form['student_code']
    return redirect(url_for('profile', student_code=student_code))
    # return render_template("profile.html", student_code = student_code)


@app.route('/instructor_portal', methods=['GET', 'POST'])
def instructor_portal():
    return render_template("instructor_entry.html")


@app.route('/post_instructor', methods = ['POST'])
def post_instructor():
    """Updates the database. Won't work for Initial Population
    Commented line will work for Initial Population"""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    grades = json.loads(populate("./static/{}".format((file.filename).replace(" ", "_"))))

    #db.reflect()
    #db.drop_all()
    #db.create_all()
    for student in grades:
        db.session.delete(User.query.filter_by(hash=student).first())
        sqlStudent = User(student, grades[student])
        # sqlStudent = User.query.filter_by(hash=student).first()
        sqlStudent.grades = grades[student]
        db.session.add(sqlStudent)
        db.session.commit()

    return "Grades Updated. Success!"


if __name__ == '__main__':
    app.run()
