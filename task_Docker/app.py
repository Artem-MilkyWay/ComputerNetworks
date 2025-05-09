from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@my_db:5432/mydb'
db = SQLAlchemy(app)

@app.route('/')
def hello():
    return "App is connected to DB!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
