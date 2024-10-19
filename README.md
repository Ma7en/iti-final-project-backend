<h1 align="center" id="title">Final Project - Frontend - Homeverse - ITI</h1>

<h2 id="description">Description</h2>

<p>
Residential Finishing Services Website Project

The "Residential Finishing Services" project is an online platform that connects users (customers) with companies specializing in home finishing services. The website aims to simplify the process of finding and contracting with trusted companies that offer comprehensive finishing services. It provides a variety of services such as interior design finishes, electrical work, plumbing, painting, and flooring installation, all tailored to the customers' needs and budgets.

Users can browse available companies, view past projects, read customer reviews, and compare different offers. Additionally, the website allows customers to request price quotes and communicate directly with companies to execute the project. The platform focuses on providing a seamless and convenient experience, ensuring high-quality service at competitive prices.

</p>

## 🔧 Github Commands :-

`Step 1` : SSH Configuration.

```
ssh-keygen -t ed25519 -C "ex@gmail.com"
```

```
cat ~/.ssh/id_ed25519.pub
```

```
git config --global user.email "ex@gmail.com"
```

```
git config --global user.name "ex"
```

`Step 2` : Starting Git.

```
git init
```

```
git add .
```

```
git commit -m "first commit"
```

```
git branch -M main
```

```
git remote add origin git@github.com:Ma7en/crowd-funding.git
```

```
git push -u origin main
```

`Step 3` : Clone.

```
git clone git@github.com:Ma7en/iti-final-project-backend.git
```

`Step 4` : Pull.

```
git pull -r origin main
```

```
Accept Both Changes
```

```
git rebase --continue
```

```
git config --global pull.rebase true
```

`Step 5` : Tag.

```
git checkout main
```

```
git tag
```

```
git tag -a v1.0 -m "Version 1.0"
```

```
git push origin v1.0
```

---

## 🛠️ Installation Steps :-

<h3 align="center"> Ubuntu </h3>

`Step 1` : Install and activate VirtualEnvironment.

```
pip install virtualenv
```

```
virtualenv venv
```

```
source venv/bin/activate
```

`Step 2` : Install Packages.

```
pip install django
```

```
pip install --upgrade pip
```

```
pip install psycopg2-binary
```

```
pip install pillow
```

```
pip install django-crispy-forms
```

```
pip install crispy-bootstrap5
```

```
pip install djangorestframework
```

```
pip install fontawesomefree
```

```
pip install django-jquery
```

```
pip install django-cleanup
```

```
pip install django-utils-six
```

```
pip install social-auth-app-django
```

```
pip install django-allauth
```

```
pip install python-dotenv
```

```
pip install django-countries
```

`Step 3` : Install requiremental Packages.

```
pip freeze > requirements.txt
```

```
pip install -r requirements.txt
```

`Step 4` : Create Project.

```
django-admin startproject homeverse
```

```
cd homeverse
```

`Step 5` : Create Apps.

```
python3 manage.py startapp api
```

`Step 6` : Create Database.

```
su - postgres
```

```
psql
```

```
CREATE USER django_proj WITH PASSWORD 'django@@1';
```

```
create database homeverse;
```

```
\c homeverse;
```

```
GRANT ALL PRIVILEGES ON DATABASE homeverse TO django_proj;
```

```
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_proj;
```

```
GRANT ALL PRIVILEGES ON SCHEMA public TO django_proj;
```

```
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_proj;
```

`Step 7` : Create Migrate.

```
python3 manage.py makemigrations
```

```
python3 manage.py migrate
```

`Step 8` : Create Superuser.

```
python manage.py createsuperuser
```

```
homeverse_proj@gmail.com
```

```
homeverse_proj
```

```
homeverse@@1
```

`Step 9` : Run Server.

```
python3 manage.py runserver
```

`Step 10` : Info Admin.

```
homeverse_proj@gmail.com
```

```
homeverse@@1
```

`Step 11` : Info Server.

```
m9ee9m+2@gmail.com
```

<h3 align="center"> Windows </h3>

`Step 1` : Install and activate VirtualEnvironment.

```
pip install virtualenv
```

```
virtualenv wvenv
```

```
wvenv\Scripts\activate
```

`Step 2` : Install Packages.

```
pip install django
```

```
pip install --upgrade pip
```

```
pip install psycopg2-binary
```

```
pip install djangorestframework
```

```
pip install pillow
```

```
asgiref
```

```
Django
```

```
django-cors-headers
```

```
djangorestframework
```

```
djangorestframework-simplejwt
```

```
PyJWT
```

```
pytz
```

```
sqlparse
```

```
psycopg2-binary
```

```
python-dotenv
```

```
pip install django-jazzmin
```

```
pip install drf-yasg
```

```
pip install --upgrade setuptools
```

```
pip install django-anymail
```

```
pip install django-storages
```

```
pip install django-ckeditor-5
```

```
pip install environs
```

```
pip install django-allauth
```

```
pip install djangorestframework-simplejwt
```

```
pip install django-crispy-forms
```

```
pip install crispy-bootstrap5
```

```
pip install fontawesomefree
```

```
pip install django-jquery
```

```
pip install django-cleanup
```

```
pip install django-utils-six
```

```
pip install social-auth-app-django
```

```
pip install django-allauth
```

```
pip install python-dotenv
```

```
pip install django-countries
```

`Step 3` : Install requiremental Packages.

```
pip freeze > wrequirements.txt
```

```
pip install -r wrequirements.txt
```

`Step 4` : Create Project.

```
django-admin startproject homeverse
```

```
cd homeverse
```

`Step 5` : Create Apps.

```
python manage.py startapp api
```

`Step 6` : Create Database.

```
su - postgres
```

```
psql
```

```
CREATE USER django_proj WITH PASSWORD 'django@@1';
```

```
create database homeverse;
```

```
\c homeverse
```

```
GRANT ALL PRIVILEGES ON DATABASE homeverse TO django_proj;
```

```
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_proj;
```

```
GRANT ALL PRIVILEGES ON SCHEMA public TO django_proj;
```

```
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_proj;
```

`Step 7` : Create Migrate.

```
python manage.py makemigrations
```

```
python manage.py migrate
```

`Step 7` : Create Superuser.

```
python manage.py createsuperuser
```

```
homeverse_proj@gmail.com
```

```
homeverse_proj
```

```
homeverse@@1
```

`Step 9` : Run Server.

```
python manage.py runserver
```

`Step 10` : Info Admin.

```
homeverse_proj@gmail.com
```

```
homeverse@@1
```

`Step 11` : Info Server.

```
m9ee9m+4@gmail.com
```

---

## 🧐 Features :

<ul>
<li>
    <b>User Authentication:</b> Secure registration, login, and password recovery.
</li>
<li>
    <b>Project Creation:</b>
</li>
<li>
    <b>Project Management:</b> Features for viewing, commenting, rating, and reporting projects.
</li>
<li>
    <b>Homepage:</b> Displays featured, latest, and categorized projects.
</li>
<li>
    <b>Search:</b> Allows users to find projects by title or tag.
</li>
<li>
    <b>Additional Features:</b> user profiles, and notifications.
</li>
</ul>

---

## 💻 Built with :-

Technologies used in the project:

-   Django Framework
-   Postgres Database

---

<p align="left"><img src="https://profile-counter.glitch.me/iti-final-project-babackend/count.svg" alt="desphixs" /></p>

---

<h1>Under The Supervision of:</h1>
<table>
    <tr>
        <td>
            <img src="https://avatars.githubusercontent.com/u/84921583?v=4"></img>
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://github.com/Ma7moudHelmi">Mahmoud Elmahmoudy</a>
        </td>
    </tr>
</table>

---

## Contributors

<table>
    <tr>
        <td>
            <img src="https://avatars.githubusercontent.com/u/91129862?v=4"></img>
        </td>
        <td>
            <img src="https://avatars.githubusercontent.com/u/120313545?v=4"></img>
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://github.com/Ma7en">Mazen Saad</a>
        </td>
        <td>
            <a href="https://github.com/rehabezzat">Rehab Ezzat</a>
        </td>
    </tr>
    <tr>
        <td>
            <img src="https://avatars.githubusercontent.com/u/93333314?v=4"></img>
        </td>
        <td>
            <img src="https://avatars.githubusercontent.com/u/174034623?v=4"></img>
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://github.com/Shrouk2000">Shrouk Ahmed</a>
        </td>
        <td>
            <a href="https://github.com/nada-mohamed-ops">Nada Mohamed</a>
        </td>
    </tr>
</table>
```
