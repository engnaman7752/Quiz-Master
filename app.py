from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Set a secret key for session management

db = SQLAlchemy(app)

# Define the userdetail table
class userdetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each user
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), unique=True, nullable=False)  # Ensure unique usernames
    password = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(120), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    questions = db.relationship('Question', backref='chapter', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=False)  # Added title field
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # "1", "2", "3", or "4"
    marks = db.Column(db.Integer, nullable=False, default=1)  # Added marks field with default value of 1
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

   
# def add_columns():
#     with app.app_context():
#         db.session.execute(text("ALTER TABLE question ADD COLUMN title VARCHAR(255) NOT NULL"))
#         db.session.execute(text("ALTER TABLE question ADD COLUMN marks INTEGER NOT NULL DEFAULT 1"))
#         db.session.commit()

# # Call the function
# add_columns()

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
    duration = db.Column(db.Integer, nullable=False)  # In minutes
    total_marks = db.Column(db.Integer, nullable=False)

    # Relationship with Chapter
    chapter = db.relationship('Chapter', backref='quizzes')

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/user', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # When the form is submitted
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Check if the username exists in the database
        user = userdetail.query.filter_by(username=username).first()

        if user:  # If the username exists
            if user.password == password:  # Check if the password matches
                session['username'] = username  # Store the username in session
                if user.role == 'user':
                    return redirect(url_for('userdash', username=username))  # Redirect to user dashboard
                else:
                    return redirect(url_for('admin', username=username))  # Redirect to admin dashboard
            else:
                return render_template("user.html", error="Incorrect password!")
        else:
            return render_template("user.html", error="Username does not exist! Register first.")

    return render_template("user.html", error=False)  # Render login form for GET request

@app.route('/newuser', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        dob_string = request.form['dob']
        dob = datetime.strptime(dob_string, '%Y-%m-%d').date()
        qualification = request.form['qualification']
        role = request.form['role']

        # Check if the username already exists
        existing_user = userdetail.query.filter_by(username=username).first()
        if existing_user:
            return render_template('newuser.html', error="Username already exists! Please use a different one.")

        # Create a new user
        new_user = userdetail(
            name=name,
            username=username,
            password=password,
            dob=dob,
            qualification=qualification,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('newuser.html', error=False)  # Render registration form for GET request

@app.route('/userdash/<username>')
def userdash(username):
    # Fetch the user by username
    user = userdetail.query.filter_by(username=username).first()
    if not user:
        return "User not found!", 404
    return render_template("userdash.html", n=user.name)

@app.route('/admin/<username>')
def admin(username):
    # Fetch the user by username
    user = userdetail.query.filter_by(username=username).first()
    
    if not user:
        return "User not found!", 404
    subjects = Subject.query.all()
    return render_template("admin.html", n=user.name,subjects=subjects)

@app.route('/start')
def start():
    return render_template("start.html")

@app.route('/addsubject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()

        # Get the current logged-in user's username from the session
        username = session.get('username')  # Retrieve the username from session
        if not username:
            return redirect(url_for('login'))  # If no user is logged in, redirect to the login page

        return redirect(url_for('admin', username=username))  # Redirect to admin page with username

    return render_template('addsubject.html')

@app.route('/addchapter/<int:subject_id>', methods=['GET', 'POST'])
def addchapter(subject_id):
    subject = Subject.query.get(subject_id)  # Get the subject by subject_id

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        username = session.get('username')  # Retrieve the username from session
        # Create a new chapter and associate it with the selected subject
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin', username=username))  # Redirect to admin page after adding chapter

    return render_template('addchapter.html', subject=subject)  # Pass the subject to the template

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)  # Get the chapter by ID

    if not chapter:
        return "Chapter not found!", 404

    db.session.delete(chapter)  # Delete the chapter from the database
    db.session.commit()
    return redirect(url_for('admin', username=session.get('username')))
@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)  # Get the chapter by ID

    if not subject:
        return "Chapter not found!", 404

    db.session.delete(subject)  # Delete the chapter from the database
    db.session.commit()
    return redirect(url_for('admin', username=session.get('username')))

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id,subject_id):
    chapter = Chapter.query.get(chapter_id)  # Get the chapter by ID
    subject = Subject.query.get(subject_id)  # Get the subject by subject_id
    if not chapter:
        return "Chapter not found!", 404

    if request.method == 'POST':
        # Update chapter details from the form
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()  # Save changes to the database
        return redirect(url_for('admin', username=session.get('username')))

    # Render the form for editing a chapter
    return render_template('addchapter.html', chapter=chapter, subject=subject)

@app.route('/quiz/<int:chapter_id>', methods=['GET','POST'])
def quiz(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return "Chapter not found!", 404

    questions = Question.query.filter_by(chapter_id=chapter_id).all()
    return render_template('quiz.html', chapter=chapter, questions=questions)

@app.route('/addquestion/<int:chapter_id>', methods=['GET', 'POST'])
def addquestion(chapter_id):
    chapter = Chapter.query.get(chapter_id)  # Fetch the chapter
    if not chapter:
        return "Chapter not found", 404  # Handle invalid chapter_id

    if request.method == 'POST':
        text = request.form['text']
        title = request.form.get('title', '')  # Added title field
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']
        marks = request.form.get('marks', 1, type=int)  # Ensure marks is an integer

        # Save to database
        new_question = Question(
            title=title,
            text=text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            marks=marks,
            chapter_id=chapter_id
        )
        db.session.add(new_question)
        db.session.commit()

        # Redirect user properly
        username = session.get('username')
        if not username:
            return redirect(url_for('login'))  # Redirect to login if not logged in
        return redirect(url_for('admin', username=username))

    # Fetch all chapters for dropdowns (if needed)
    chapters = Chapter.query.all()
    return render_template('addquestion.html', chapter=chapter, chapters=chapters)

@app.route('/newquiz', methods=['GET', 'POST'])
def new_quiz():
    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        quiz_date = request.form['quiz_date']
        duration = request.form['quiz_time']
        total_marks = request.form['quiz_marks']

        # Validate input
        if not chapter_id or not quiz_date or not duration or not total_marks:
            return render_template('NewQuiz.html', error="All fields are required!")

        # Store quiz details in the database
        new_quiz = Quiz(
            chapter_id=chapter_id,
            quiz_date=datetime.strptime(quiz_date, '%Y-%m-%d').date(),
            duration=int(duration),
            total_marks=int(total_marks)
        )
        db.session.add(new_quiz)
        db.session.commit()

        username = session.get('username')
        if not username:
            return redirect(url_for('login'))

        return redirect(url_for('admin', username=username))  # Redirect to admin page with username

    chapters = Chapter.query.all()
    return render_template('NewQuiz.html', chapters=chapters, error=None)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('login'))  # Redirect to login page

if __name__ == "__main__":
    app.run(debug=True, port=8000)
