# Online Examination System

A full-stack web-based **Online Examination System** developed using **Python, Flask, SQLAlchemy, HTML, CSS, and JavaScript**.

The system provides separate functionalities for teachers and students. Teachers can create and manage examinations, while students can attempt examinations online and view their results after evaluation.

## Features

### Teacher Module
- Teacher authentication
- Create examinations
- Add and manage questions
- Support for MCQ, True/False, Short Answer, and Long Answer questions
- Publish examinations
- View student submissions
- Evaluate descriptive answers
- Publish student results

### Student Module
- Student authentication
- View available examinations
- Attempt examinations online
- Answer different types of questions
- Auto-save answers
- Submit examinations
- View results after teacher evaluation

### Evaluation
- Automatic evaluation of objective questions
- Teacher evaluation of descriptive answers
- Automatic score and percentage calculation
- Result publishing

## Technology Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF

**Frontend**
- HTML
- CSS
- JavaScript
- Jinja2 Templates

**Database**
- SQLite for local development
- PostgreSQL for deployment

**Deployment**
- Render

## Project Structure

```text
online_exam_system/
│
├── app/
│   ├── auth/
│   ├── main/
│   ├── student/
│   ├── teacher/
│   ├── models/
│   ├── templates/
│   ├── extensions.py
│   └── __init__.py
│
├── config.py
├── requirements.txt
├── run.py
├── README.md
└── .gitignore
