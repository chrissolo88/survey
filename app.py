from flask import Flask, request, render_template, redirect, flash, session, make_response
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
    survey_key = session['survey_key']
    if session.get('started') == None:
        session['started'] = []
    started = session['started']
    if survey_key not in started:
        started.append(survey_key)
        session['started'] = started
    if session.get('finished'):
        for survey_resp in session['finished']:
            if survey_key in survey_resp:
                flash(f"Looks like you already completed {survey_key}")
                return redirect('/end')
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
    
    if session.get('finished') == None:
        session['finished'] = []
        
    finished = session['finished']
    
    for survey_resp in finshed:
        if survey_key in survey_resp:
            responses = survey_resp[1]
            
    if [survey_key,responses] not in finished:
        finished.append([survey_key,responses])
        session['finished'] = finished
    num = len(responses)
       
    return render_template('end.html', num=num, responses=responses, questions=questions)
