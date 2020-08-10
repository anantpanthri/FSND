## Content

1. [Motivation](#motivation)
2. [Local Setup](#local_setup)
3. [API endpoints](#api)
4. [Authentification](#authentification)
5. [Deployment](#deployment)


<a name="motivation"></a>
## Motivation
1. Architect relational database models in Python
2. Utilize SQLAlchemy to conduct database queries
3. Follow REST ful principles of API development
4. Structure endpoints to respond to four HTTP methods, including error handling
5. Enable Role Based Authentication and roles-based access control (RBAC) in a Flask application
6. Application is hosted live on heroku





<a name="local_setup"></a>
## Local setup
#### Actors
The below endpoint will query all the actors in the database
##### End Point
 `http://localhost:5000/actors`
#### GET
`{
    "actors": [
        {
            "age": 29,
            "gender": "Male",
            "id": 1,
            "name": "Anant"
        }
        ],
    "success": true
}`
#### Create Actor
##### End Point
 `http://localhost:5000/actors`
##### POST
`
        {
            "age": 30,
            "gender": "Female",
            "name": "Anjelina"
        }
  `
##### OUTPUT
`{
    "created": 6,
    "success": true
}`
#### Get Movies

##### End Point
`http://localhost:5000/movies`
##### Output
`{
    "movies": [
        {
            "id": 1,
            "release_date": "Mon, 10 Aug 2020 00:00:00 GMT",
            "title": "Steps to code"
        }
    ],
    "success": true
}`


