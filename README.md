**StudySphere**
A simple study companion web app built with Flask and SQLite as a college semester project. It helps students keep track of tasks, monitor their progress through subjects, plan for exams, and test themselves with quizzes.

**Features**
- Dashboard: pending and overdue tasks, overall progress, and your last quiz score at a glance
- Tasks: add to-dos with due dates, mark them done, and delete them
- Progress tracker: organise work into subjects and topics, tick off what you've studied, and see a completion percentage per subject
- Study planner: enter an exam date and get your unfinished topics spread evenly over the days left
- Quizzes: random multiple-choice quizzes per subject, loaded from a CSV file, with scores saved

**Tech stack**
- Python 3.12
- Flask
- SQLite
- pytest (with GitHub Actions running the tests automatically)

**Getting started**
1. Clone the repository:
   ```
   git clone https://github.com/<owner>/studysphere.git
   cd studysphere
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac / Linux
   ```
3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.
The database (`studysphere.db`) is created automatically on the first run, with some sample data.

**Running the tests**
```
pytest
```

**Project structure**
```
app.py          Flask routes
logic/          Application logic (tasks, progress, planner, quiz, validators)
templates/      HTML pages
static/         CSS
data/           Quiz questions (quiz_data.csv)
tests/          Automated tests
schema.sql      Database tables
```

**Adding quiz questions**
Questions live in `data/quiz_data.csv` with the columns `subject,quiz,question,a,b,c,d,answer`. The `answer` column is the letter of the correct option (A, B, C or D).
