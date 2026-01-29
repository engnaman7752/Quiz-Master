import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)

# Production config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '7af2c690aae6babb4dbae4cb939fa0fd5bccaf86498f1d540390f44d1d2a7cca')

# Database config with PostgreSQL support
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class userdetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(120), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    questions = db.relationship('Question', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    marks = db.Column(db.Integer, nullable=False, default=1)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetail.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    chapter = db.relationship('Chapter', backref='quizzes')

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return redirect(url_for('user'))

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = userdetail.query.filter_by(username=username).first()
        
        if user and user.password == password and user.role == role:
            session['username'] = username
            session['role'] = role
            
            if role == 'admin':
                return redirect(url_for('admin', username=username))
            else:
                return redirect(url_for('userdash', username=username))
        else:
            return render_template('user.html', error='Invalid credentials or role')
    
    return render_template('user.html')

@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')
        role = request.form.get('role')
        
        existing_user = userdetail.query.filter_by(username=username).first()
        if existing_user:
            return render_template('newuser.html', error='Username already exists')
        
        dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        
        new_user = userdetail(
            name=name,
            username=username,
            password=password,
            qualification=qualification,
            dob=dob_date,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('user'))
    
    return render_template('newuser.html')

@app.route('/userdash/<username>')
def userdash(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('user'))
    
    return render_template('userdash.html', n=username)

@app.route('/admin/<username>')
def admin(username):
    if 'username' not in session or session['username'] != username or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    subjects = Subject.query.all()
    
    for subject in subjects:
        for chapter in subject.chapters:
            chapter.num_questions = len(chapter.questions)
    
    return render_template('admin.html', n=username, subjects=subjects)

@app.route('/addsubject', methods=['GET', 'POST'])
def addsubject():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('addsubject.html')

@app.route('/addchapter/<int:subject_id>', methods=['GET', 'POST'])
def addchapter(subject_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('addchapter.html', subject=subject, chapter=None)

@app.route('/addquestion/<int:chapter_id>', methods=['GET', 'POST'])
def addquestion(chapter_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    chapters = Chapter.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        marks = request.form.get('marks')
        selected_chapter_id = request.form.get('chapter_id')
        
        new_question = Question(
            title=title,
            text=text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            marks=int(marks),
            chapter_id=int(selected_chapter_id)
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        return redirect(url_for('quiz', chapter_id=selected_chapter_id))
    
    return render_template('addquestion.html', chapter=chapter, chapters=chapters)

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    
    return redirect(url_for('admin', username=session['username']))

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    
    return redirect(url_for('admin', username=session['username']))

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = chapter.subject
    
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('addchapter.html', subject=subject, chapter=chapter)

@app.route('/quiz/<int:chapter_id>', methods=['GET', 'POST'])
def quiz(chapter_id):
    if 'username' not in session:
        return redirect(url_for('user'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    questions = chapter.questions
    
    if request.method == 'POST':
        return redirect(url_for('admin', username=session['username']))
    
    return render_template('quiz.html', chapter=chapter, questions=questions)

@app.route('/newquiz', methods=['GET', 'POST'])
def new_quiz():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('user'))
    
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        quiz_date = request.form.get('quiz_date')
        duration = request.form.get('duration')
        total_marks = request.form.get('total_marks')
        
        quiz_date_obj = datetime.strptime(quiz_date, '%Y-%m-%d').date()
        
        new_quiz = Quiz(
            chapter_id=int(chapter_id),
            quiz_date=quiz_date_obj,
            duration=int(duration),
            total_marks=int(total_marks)
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        return redirect(url_for('admin', username=session['username']))
    
    chapters = Chapter.query.all()
    return render_template('NewQuiz.html', chapters=chapters)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user'))

# Health check endpoint
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

# Production server config
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)