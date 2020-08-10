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
### Actors
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
The below endpoint will create an actor in the database

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
#### Update Actor
The below endpoint will update an actor in the database

##### End Point
 `http://localhost:5000/actors/2`
##### PATCH
`
        {
            "age": 50,
            "gender": "Male",
            "name": "SRK"
        }
  `
##### OUTPUT
`{
    "actor": [
        {
            "age": 50,
            "gender": "Male",
            "id": 2,
            "name": "SRK"
        }
    ],
    "success": true,
    "updated": "SRK"
}`

#### delete Actor
The below endpoint will delete an actor in the database

##### End Point
 `http://localhost:5000/actors/2`
##### DELETE
##### OUTPUT
`{
    "deleted": "2",
    "success": true
}`


#### Get Movies
The below endpoint will query all the movies in the database

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
#### Create Movies
The below endpoint will create a movie in the database

##### End Point
 `http://localhost:5000/movies`
##### POST
`
        {
            "release_date": "Mon, 10 Aug 2020 00:00:00 GMT",
            "title": "Hello brother!!!"
        }
  `
##### OUTPUT
`{
    "created": "Hello brother!!!",
    "success": true
}`
#### Delete Movies
The below endpoint will delete a movie in the database

##### End Point
 `http://localhost:5000/movies/7`
##### DELETE
##### OUTPUT
`{
    "deleted": "7",
    "success": true
}`

#### Update Movies
The below endpoint will update a movie in the database

##### End Point
 `http://localhost:5000/movies/10`
##### PATCH
`
        {
            "release_date": "Mon, 10 Aug 2020 00:00:00 GMT",
            "title": "Stigma in society"
        }
  `
##### OUTPUT
`{
    "edited": 10,
    "movie": [
        {
            "id": 10,
            "release_date": "Mon, 10 Aug 2020 00:00:00 GMT",
            "title": "Stigma in society"
        }
    ],
    "success": true
}`
