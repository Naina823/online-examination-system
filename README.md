# Online Examination System

A full-stack web-based Online Examination System developed using Python, Flask, SQLAlchemy, HTML, CSS, and JavaScript.

The system provides separate functionalities for teachers and students. Teachers can create, manage, and publish examinations, while students can view available examinations, attempt them online, submit their answers, and view their results after evaluation.

## Features

### Teacher Module

- Teacher registration and login
- Teacher dashboard
- Create examinations
- Configure examination details
- Add questions to examinations
- Support for multiple question types
- MCQ questions
- True/False questions
- Short Answer questions
- Long Answer questions
- Edit and manage examination questions
- Publish examinations
- View student submissions
- Evaluate descriptive answers
- Publish student results

### Student Module

- Student registration and login
- Student dashboard
- View available examinations
- View examination details
- Start an examination
- Attempt questions online
- Answer MCQ questions
- Answer True/False questions
- Answer Short Answer questions
- Answer Long Answer questions
- Auto-save student answers
- Submit examination
- View submission status
- View results after the teacher publishes them

### Evaluation System

- Automatic evaluation of objective questions
- Automatic evaluation of MCQ questions
- Automatic evaluation of True/False questions
- Teacher evaluation of descriptive answers
- Score calculation
- Percentage calculation
- Result management
- Result publishing to students

### Authentication and Security

- User registration
- User login and logout
- Password-based authentication
- Role-based access for teachers and students
- Protected routes
- Flask-Login authentication
- CSRF protection using Flask-WTF

## Examination Workflow

The complete examination workflow is:

Teacher Registration/Login
        ↓
Teacher Dashboard
        ↓
Create Examination
        ↓
Add Questions
        ↓
Publish Examination
        ↓
Student Login
        ↓
Student Dashboard
        ↓
View Available Examination
        ↓
Start Examination
        ↓
Answer Questions
        ↓
Auto-Save Answers
        ↓
Submit Examination
        ↓
Automatic Evaluation of Objective Questions
        ↓
Teacher Evaluates Descriptive Answers
        ↓
Score and Percentage Calculation
        ↓
Teacher Publishes Result
        ↓
Student Views Result

## Technology Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- WTForms

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

### Database

- SQLite for local development
- PostgreSQL for production deployment

### Deployment

- Render

### Version Control

- Git
- GitHub

## Database Models

The application uses SQLAlchemy models to manage the examination system data.

The main models include:

- User
- Exam
- Question
- QuestionOption
- ExamQuestion
- ExamAttempt
- StudentAnswer

### User

Stores user information and user roles such as teacher and student.

### Exam

Stores examination information such as examination title, duration, status, and other examination details.

### Question

Stores questions belonging to an examination and supports different question types.

### QuestionOption

Stores answer options for objective questions such as MCQ and True/False questions.

### ExamQuestion

Associates questions with examinations.

### ExamAttempt

Stores information about a student's attempt of an examination.

### StudentAnswer

Stores the answers submitted by students during an examination.

## Project Structure

```text
online_exam_system/
│
├── app/
│   │
│   ├── auth/
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── main/
│   │   └── routes.py
│   │
│   ├── student/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── teacher/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── exam.py
│   │   ├── question.py
│   │   ├── question_option.py
│   │   ├── exam_question.py
│   │   ├── exam_attempt.py
│   │   └── student_answer.py
│   │
│   ├── templates/
│   │   ├── auth/
│   │   ├── student/
│   │   ├── teacher/
│   │   ├── base.html
│   │   └── home.html
│   │
│   ├── __init__.py
│   └── extensions.py
│
├── config.py
├── requirements.txt
├── run.py
├── README.md
└── .gitignore
Installation
1. Clone the Repository

Clone the project from GitHub:

git clone https://github.com/Naina823/online-examination-system.git
2. Navigate to the Project Directory
cd online-examination-system
3. Create a Virtual Environment
python -m venv .venv
4. Activate the Virtual Environment

For Windows:

.venv\Scripts\activate

For macOS/Linux:

source .venv/bin/activate
5. Install Dependencies

Install all required Python packages using:

pip install -r requirements.txt
6. Run the Application

Start the Flask application using:

python run.py
7. Open the Application

After starting the application, open the following address in a web browser:

http://127.0.0.1:5000
Requirements

The project requires Python and the dependencies listed in requirements.txt.

The main dependencies include:

Flask
Flask-SQLAlchemy
Flask-Login
Flask-WTF
WTForms
email-validator
Gunicorn
Psycopg
Local Database

During local development, the application uses SQLite as the database.

The local database is stored inside the application's instance directory and is excluded from Git using .gitignore.

Production Database

For deployment, the application uses PostgreSQL.

The database connection is configured through the DATABASE_URL environment variable.

The application configuration supports both local SQLite development and PostgreSQL production deployment.

Environment Variables

The application uses environment variables for production configuration.

The following environment variables are required for deployment:

SECRET_KEY
DATABASE_URL
SECRET_KEY

SECRET_KEY is used by Flask for security-related functionality such as sessions and CSRF protection.

DATABASE_URL

DATABASE_URL contains the connection information for the PostgreSQL database used by the deployed application.

Deployment

The application can be deployed using Render.

The deployment process consists of:

Push the project to GitHub.
Create a PostgreSQL database on Render.
Create a Render Web Service.
Connect the Web Service to the GitHub repository.
Select the main branch.
Set the build command:
pip install -r requirements.txt
Set the start command:
gunicorn run:app
Configure the required environment variables.
Add the PostgreSQL DATABASE_URL.
Add a secure SECRET_KEY.
Deploy the application.

After successful deployment, Render provides a public URL through which the Online Examination System can be accessed.

Application Workflow
Teacher Workflow
Teacher registers or logs in.
Teacher accesses the teacher dashboard.
Teacher creates an examination.
Teacher adds questions.
Teacher publishes the examination.
Students can then see the published examination.
Teacher views student submissions.
Teacher evaluates descriptive answers.
Teacher publishes the final result.
Students can view their published results.
Student Workflow
Student registers or logs in.
Student accesses the student dashboard.
Student views available examinations.
Student selects an examination.
Student starts the examination.
Student answers the questions.
Student answers are auto-saved during the examination.
Student submits the examination.
Objective questions are evaluated automatically.
Descriptive answers are evaluated by the teacher.
The final score and percentage are calculated.
The student can view the result after it is published.
Security

The application includes authentication and authorization features to protect different parts of the system.

Flask-Login is used for user authentication.
Login-required routes are protected.
Teacher and student functionalities are separated using roles.
Flask-WTF provides CSRF protection.
Secret configuration values are stored using environment variables during deployment.
Database credentials are not stored directly in the source code.
Purpose of the Project

The purpose of this project is to develop a complete web-based Online Examination System that simplifies the process of conducting examinations digitally.

The system provides a platform where teachers can create and manage examinations, students can participate in examinations online, objective questions can be evaluated automatically, descriptive answers can be evaluated by teachers, and final results can be published to students.

The project demonstrates the practical implementation of:

Web application development
Flask framework
Database management
Object-relational mapping
Authentication
Role-based authorization
Online examination management
Automatic evaluation
Teacher-based evaluation
Result management
Cloud deployment
Future Scope

The system can be further enhanced in the future with additional features such as:

Email notifications
Advanced analytics
Examination reports
Question bank management
Random question selection
Advanced anti-cheating mechanisms
Student performance analytics
Administrative dashboard
Certificate generation
Author

Naina823

License

This project is developed for academic and educational purposes.


### After you paste it

Click:

**Commit changes → Commit changes**

That's all. ✅

Then your GitHub repository will have a proper professional README, and we can **immediately move to Render depl
