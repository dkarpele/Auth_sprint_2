# Service API (Auth and Content).

It provides the service to work with users and their roles: create, update and delete; user login. Changing user roles. An API to work with films, persons and genres.

## What was done in this sprint:
* Auth using social logins (Google and Yandex)
* Requests Rate limit to the server. Using algorithm Leaky bucket. Requests that exceed limit receive HTTP-status 429 Too Many Requests.
* Tracer with the help from Jaeger
* Auth integration with Django and content endpoint /api/v1/films/<film_id>

## Project structure:

* Auth API service - uses FastApi Async framework to provide API for external services. The service uses FastApi for API, Postgres to store user data and roles, and Redis for caching invalid access tokens and refresh tokens. The first thing to do is to create _admin_ user and _admin_ role (use `docker-compose up`):
* Content API service -  uses FastApi Async framework to provide API for external services. It loads data from ElasticSearch or cached data from Redis.
* Django - admin panel
* tests - pytest based tests for API


## Documentation

[OpenAPI](http://localhost/api/openapi) documentation is available after creating the service.


## Installation

1. Clone [repo](https://github.com/dkarpele/Auth_sprint_2).
2. Create ```.env``` file according to ```.env.example```.
3. Launch the project ```docker-compose up --build```.


## Development Auth API
1. Clone [repo](https://github.com/dkarpele/Auth_sprint_2).
2. Create ```.env``` file according to ```.env.example```.
3. Launch the project ```docker-compose up postgres redis```.
4. Apply migrations ```cd src ; alembic upgrade head```
5. Create admin user ```python3 create-admin.py```
6. Launch the server from _/src_: ```python3 main.py``` 


## Testing

1. Go to `/tests/functional`
2. Create ```.env``` file according to ```.env.example```.
3. Launch the project ```docker-compose up --build```.


## API calls

auth:

- POST http://127.0.0.1/api/v1/auth/signup - create new account.
- POST http://127.0.0.1/api/v1/auth/login - log in as current user. Returns tokens.
- POST http://127.0.0.1/api/v1/auth/logout - logout (must be authorised).
- POST http://127.0.0.1/api/v1/auth/refresh - receive a new pair of tokens
- POST http://127.0.0.1/api/v1/auth/login-sso - _[NEW]_: log in as current user. Returns user. It uses by Django to log in to admin panel from external Auth system.

oauth:

- GET http://127.0.0.1/api/v1/oauth/signup/{service_name} - _[NEW]_: Signup with Service provider: Google or Yandex 

roles:

(only for _admin_ role, must be authorised)
- GET http://127.0.0.1/api/v1/roles/ - receive list of all available roles in DB
- POST http://127.0.0.1/api/v1/roles/create - create new role
- PATCH http://127.0.0.1/api/v1/roles/<role_id> - update role
- DELETE http://127.0.0.1/api/v1/roles/<role_id> - delete role

users:

- POST http://127.0.0.1/api/v1/users/add-role - add role to user (only for _admin_ role)
- DELETE http://127.0.0.1/api/v1/users/delete-role - remove role from user (only for _admin_ role)
- GET http://127.0.0.1/api/v1/users/roles - list all roles for current user (only for _admin_ role)
- GET http://127.0.0.1/api/v1/users/me - get all data about current user (must be authorised)
- POST http://127.0.0.1/api/v1/users/change-login-password - change user's login/password (must be authorised)
- GET http://127.0.0.1/api/v1/users/login-history - list user's login history (must be authorised)

films:

- GET http://127.0.0.1/api/v1/films/ - receive list of all available films in ES
- GET http://127.0.0.1/api/v1/films/<film_id> - get film by id. _[NEW]_: Access token must be provided to use the method. For demo purposes it will work only for roles admin and manager.
- GET http://127.0.0.1/api/v1/films/search - Search film by title

genres:

- GET http://127.0.0.1/api/v1/genres/ - receive list of all available genres in ES
- GET http://127.0.0.1/api/v1/genres/<genre_id> - get genre by id

persons:

- GET http://127.0.0.1/api/v1/persons/search - Search person by name
- GET http://127.0.0.1/api/v1/persons/<person_id> - Person's data
- GET http://127.0.0.1/api/v1/persons/<person_id>/film - list of films for person


## Authors
* Lubov Sovina [@lubovSovina](https://github.com/lubovSovina)
* Denis Karpelevich [@dkarpele](https://github.com/dkarpele)
