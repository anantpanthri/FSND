psql # Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
1. For booting up the database make sure that you have postgres installed
```bash
% postgres -V
    postgres (PostgreSQL) 12.3
```
2. DB setup
database_name = "trivia"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

3. Starting and Stopping postgres
```bash
pg_ctl -D /usr/local/var/postgres stop
pg_ctl -D /usr/local/var/postgres start
```

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
$ createdb trivia
$ createdb trivia_test
$ psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## API endpoints 
Base URL ```http://127.0.0.1:5000/```

#### 1. GET '/categories'
``http://127.0.0.1:5000/categories``

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 

```
Sample Response
{
  "categories": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "success": true
}
```

#### 2. GET '/questions'
```
http://127.0.0.1:5000/questions?page=1
```

- Fetches a dictionary of questions in which the keys are the ids list of categories total number of questions as the response is paginated for 10 questions per page
- Request Arguments: page=1 <Integer>
- Returns: An object of categories, current categories where questions belong, 
    object of questions
                -id:<Inetger> unique id for the question
                -question:<String> question
                -answer:<String> answer to the question
                -category:<String> tells which category the question belongs
                -difficulty:<Inetger> marks the difficulty of the question
    total questions-<Integer> total number of questions


```
Sample response
{
  "categories": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "current_category": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {...}
  ], 
  "success": true, 
  "total_questions": 27
}
```
#### Errors

```http://127.0.0.1:5000/questions?page=1343```

```
{
  "error": 404, 
  "message": "resource not found", 
  "success": false
}
```

#### 3. DELETE '/questions/<int:question_id>'

``curl -X DELETE http://127.0.0.1:5000/questions/2``
Deletes the question 
Request
    Method: Delete
    <questionid>:Integer question id to be deleted 
Response
    success: true if id is found
             false if id not found or database is disconnected 

```

{
  "deleted_question_id": 2, 
  "success": true
}
```
#### Errors
```
curl -X DELETE http://127.0.0.1:5000/questions/4
{
  "error": 404, 
  "message": "resource not found", 
  "success": false
}

```

#### 4 search or create questions '/questions'
Searches the question if the question is not in the database adds it.
This endpoint will search based on the pattern so if matches partially or completely returns the result
Method:POST
Request param:if search json body
 ````
Request Sample
{'searchTerm': 'discovered'}
   
 ````
Response:
    current_category: category the question belongs
    questions: question object
```
Response Sample
{
  "current_category": [
    1
  ], 
  "questions": [
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }
  ], 
  "success": true, 
  "total_questions": 26
}

```
Request Param   if adding a question json body of question object is required
                
```
Sample request object
{
'question': 'where is delhi', 
'answer': 'india', 
'difficulty': '4', 
'category': '2'
}
```
``` 
Response
"POST /questions HTTP/1.1" 200 
```

#### 5 Get questions based on categories  /categories/<string:category_id>/questions
Gets the question based on the categories
Method GET ```curl -X GET  http://127.0.0.1:5000/categories/2/questions```

Request param string:category_id
    category_id can be [1,2,3,4,5]

```
Response Sample
{
  "current_category": "2", 
  "questions": [
    {
      "answer": "Escher", 
      "category": 2, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {...}
}

```
#### 6 Play Quiz  /quizzes
Gets the question based on the categories
Method POST 
Request param 
``curl -X POST http://127.0.0.1:5000/quizzes -d '{"previous_questions" : [1, 2, 5], "quiz_category" : {"type" : "Science", "id" : "1"}} ' -H 'Content-Type: application/json'``


```
Sample Response
{
  "question": {
    "answer": "The Palace of Versailles", 
    "category": 3, 
    "difficulty": 3, 
    "id": 14, 
    "question": "In which royal palace would you find the Hall of Mirrors?"
  }, 
  "success": true
}

```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
The test cases are located in test_flaskr.py
```

Launching unittests with arguments python -m unittest /Users/anantpanthri/PycharmProjects/FSND/projects/02_trivia_api/starter/backend/test_flaskr.py in /Users/anantpanthri/PycharmProjects/FSND/projects/02_trivia_api/starter/backend

Process finished with exit code 0
/Users/anantpanthri/workspace_Python/venv/lib/python3.8/site-packages/sqlalchemy/util/langhelpers.py:253: SADeprecationWarning: The 'postgres' dialect name has been renamed to 'postgresql'
  loader = self.auto_fn(name)

Ran 8 tests in 0.333s
OK


```
