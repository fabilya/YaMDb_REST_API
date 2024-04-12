# REST API for YaMDb
REST API for the YaMDb service — movie, book and music reviews database.
### Description
The YaMDb project collects user reviews for compositions. Compositions are divided into categories such as "Books", "Films", "Music". Administrators can add new categories.
Compositions themselves are not stored in YaMDb, you can't watch a movie or listen to a song here.
Each composition can be assigned with genres from the predefined list (for example, "Fairy Tale", "Rock" or "Arthouse"). Administrators can also add new genres.
Users can add reviews for every composition with a personal score. They can also comment each other reviews.
The average rating is automatically calculated for each composition.
#### User Roles
* Anonymous — can read compositions, reviews and comments.
* Authenticated user — can also publish reviews with personal score and comment reviews. Can edit and delete own reviews and comments. This role is assigned by default to every new user.
* Moderator — can also delete any review or comment.
* Administrator — has full rights to manage all project content. Can create and delete compositions, categories and genres. Can assign user roles.
* Django Superuser is always an administrator.
#### Full API documentation is available after installation:
[http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
### Technology stack:
* Python 3.9
* Django 3.2
* DRF 3.12.4
* JWT
### Installation
* Clone repository:
```
git clone git@github.com:MicroElf/api_yamdb.git
```
* Install and activate virtual environment with Python 3.9:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
* Install all dependencies from requirements.txt
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
* Apply migrations:
```
python manage.py migrate --run-syncdb
```
* Create a superuser:
```
python manage.py createsuperuser
```
* If you need fill the database with test data:
```
python manage.py importcsv
```
* Run project:
```
python manage.py runserver localhost:80
```
### API examples
For unauthorized users, working with the API is available in read mode. It will not be possible to create or change anything.  

Permissions: Available without a token.  
GET `/api/v1/categories/` — Get a list of all categories  
GET `/api/v1/genres/` — Get a list of all genres  
GET `/api/v1/titles/` — Get a list of all titles  
GET `/api/v1/titles/{title_id}/reviews/` — Get a list of all reviews  
GET `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` — Get a list of all comments on a review

Permissions: Administrator  
GET `/api/v1/users/` — Get a list of all users
## Participants
Group student project during education at Yandex.Practicum  
* ✅ [Evgeny "MicroElf" Chernykh](https://github.com/MicroElf) (Teamlead)  
* ✅ [Ilya "Fabilya" Fabiyansky](https://github.com/fabilya) (Python Developer)
