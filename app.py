from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UserDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # More fields can be added as per requirement

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    chapters = db.relationship('Chapter', backref='subject', cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    questions = db.relationship('Question', backref='chapter', cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question', backref='quiz', cascade='all, delete-orphan')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Example routes
@app.route('/login', methods=['POST'])
def login():
    # Login logic here
    return jsonify({'message': 'Logged in successfully'}), 200

@app.route('/register', methods=['POST'])
def register():
    # Registration logic here
    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/userdash')
def userdash():
    return jsonify({'message': 'User Dashboard'}), 200

@app.route('/admin')
def admin():
    return jsonify({'message': 'Admin Dashboard'}), 200

@app.route('/addsubject', methods=['POST'])
def addsubject():
    # Add subject logic here
    return jsonify({'message': 'Subject added'}), 201

@app.route('/addchapter', methods=['POST'])
def addchapter():
    # Add chapter logic here
    return jsonify({'message': 'Chapter added'}), 201

@app.route('/delete_chapter/<int:id>', methods=['DELETE'])
def delete_chapter(id):
    # Delete chapter logic here
    return jsonify({'message': 'Chapter deleted'}), 200

@app.route('/delete_subject/<int:id>', methods=['DELETE'])
def delete_subject(id):
    # Delete subject logic here
    return jsonify({'message': 'Subject deleted'}), 200

@app.route('/edit_chapter/<int:id>', methods=['PUT'])
def edit_chapter(id):
    # Edit chapter logic here
    return jsonify({'message': 'Chapter edited'}), 200

@app.route('/quiz')
def quiz():
    return jsonify({'message': 'Quiz endpoint'}), 200

@app.route('/addquestion', methods=['POST'])
def addquestion():
    # Add question logic here
    return jsonify({'message': 'Question added'}), 201

@app.route('/newquiz', methods=['POST'])
def newquiz():
    # Create new quiz logic here
    return jsonify({'message': 'New quiz created'}), 201

@app.route('/logout', methods=['POST'])
def logout():
    # Logout logic here
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))