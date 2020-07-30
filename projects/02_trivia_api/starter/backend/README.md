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

## Tasks


One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

##API endpoints 
Base URL ```http://127.0.0.1:5000/```



####1. GET '/categories'
``http://127.0.0.1:5000/categories``
```
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
```
```
Example Response
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

####2. GET '/questions'
```
http://127.0.0.1:5000/questions?page=1
```
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

```
Example response
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
####Errors

```http://127.0.0.1:5000/questions?page=1343```

```
{
  "error": 404, 
  "message": "resource not found", 
  "success": false
}
```

####3. DELETE '/questions/<int:question_id>'

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
####Errors
```
curl -X DELETE http://127.0.0.1:5000/questions/4
{
  "error": 404, 
  "message": "resource not found", 
  "success": false
}

```

####4 search or create questions '/questions'
searches the question if the question is not in the database adds it.
This endpoint will search based on the pattern so if matches partially or completely returns the result
Method:POST
Request param:if search json body
 ````
Request Example
{'searchTerm': 'discovered'}
   
 ````
Response:
    current_category: category the question belongs
    questions: question object
```
Response Example
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

####5 Get questions based on categories  /categories/<string:category_id>/questions


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

