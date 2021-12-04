# PayUp

**Deployment:** Try it with heroku [here](http://payup-sprint-2.herokuapp.com/login)

## Introduction
Signup to track your expenses. Login anytime to add or remove your budget and expenses.

![image](https://user-images.githubusercontent.com/89946346/144693501-80aaeec4-3f3a-43a5-a4c8-3ef908506f60.png)
![image](https://user-images.githubusercontent.com/89946346/144693511-ade995ec-7917-4c37-8b4b-cfbe4a9fa07e.png)

## Setup Instruction
- To run the project clone it into local directory create a ```.env``` file containing below mentioned parameters
```
DATABASE_URL -> URL for database
SECRET_KEY -> can be anystring or you can literally smash the keyboard
EMAIL_USER -> an email address
EMAIL_PASSWD -> email address password
```
- Install all the requirements from ```requierements.txt```
```bash 
Pillow
flask_bcrypt
flask_wtf
flask_login
wtforms
flask_mail
email_validator
python_dotenv
flask_sqlalchemy
psycopg2-binary
base
sqlalchemy
```

## To run the app
You can start the project by executing ```python app.py``` or ```python3 app.py```command

## Linting
You can ignore: 
``` bash
- C0103 (invalid-name) (Because the problem is only the capitalization of variable name)
- E1101 (no-member) (It's a bug between pylint and flask SQLAlchemy)
- R0903 (too-few-public-methods) (Because pylint wanted at least 2 public method for each class)
- R0201 (no-self-use) (Pylint is suggesting that the method could be used as a static function instead)
```