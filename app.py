from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = 'surveys1234'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

@app.route('/')
def start_page():
    return render_template('start.html', surveys=surveys)

@app.route('/title', methods=["POST"])
def title_page():
    survey_key = request.form['survey']
    session['survey_key'] = survey_key
    title = surveys[survey_key].title
    instructions = surveys[survey_key].instructions
    return render_template('title.html', title=title, instructions=instructions)

@app.route("/new")
def new_responses():
    session['responses'] = []
    return redirect("/question/0")

@app.route('/question/<int:number>')
def question_display(number):
    survey_key = session.get('survey_key')
    responses = session.get('responses')
    if len(surveys[survey_key].questions) == len(responses):
        return redirect('/end')
    elif number == len(responses):
        question = surveys[survey_key].questions[number].question
        choices = surveys[survey_key].questions[number].choices
        allow_text = surveys[survey_key].questions[number].allow_text
        print(question, number, choices)
        return render_template('question.html',question=question,number=number,choices=choices, allow_text=allow_text)
    else:
        flash(f"Invalid question, redirecting to '/question/{len(responses)}'")
        return redirect(f'/question/{len(responses)}')

@app.route('/answer',methods=["POST"])
def record_answer():
    survey_key = session['survey_key']
    responses = session['responses']
    if request.form.get('comment'):
        comment = request.form.get('comment')
        responses.append((request.form['answer'],comment))
    else:
        responses.append(request.form['answer'])
    session['responses'] = responses
    
    print(session['responses'])
    if len(surveys[survey_key].questions) > len(responses):
        return redirect(f'/question/{len(responses)}')
    else:
        return redirect('/end')
    
@app.route('/end')
def thanks_page():
    survey_key = session['survey_key']
    responses = session['responses']
    questions = surveys[survey_key].questions
    num = len(responses)
    print(type(responses[3]))
    return render_template('end.html', num=num, responses=responses, questions=questions)