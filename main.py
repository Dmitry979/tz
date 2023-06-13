import requests
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)  # Создание экземпляра приложения Flask
api = Api(app)  # Создание экземпляра API, связанного с приложением Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tehtz.db'  # Установка URI базы данных SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений в базе данных
db = SQLAlchemy(app)  # Создание экземпляра SQLAlchemy, связанного с приложением Flask

# Определение модели данных для таблицы в базе данных
class Baza(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Поле ID с автоинкрементом
    id_question = db.Column(db.Integer)  # Поле для ID вопроса
    question = db.Column(db.Text)  # Поле для текста вопроса
    answer = db.Column(db.Text)  # Поле для текста ответа
    created_at = db.Column(db.DateTime)  # Поле для даты создания вопроса

    def __repr__(self):
        return self.question  # Метод, возвращающий строковое представление объекта модели

# Определение ресурса API для обработки POST-запросов
class Main(Resource):
    def post(self, id_):
        parser = reqparse.RequestParser()  # Создание парсера аргументов запроса
        parser.add_argument('questions_num', type=int)  # Определение аргумента questions_num с типом int
        args = parser.parse_args()  # Разбор аргументов запроса
        questions_num = args['questions_num']  # Получение значения аргумента questions_num

        response = requests.get(f'https://jservice.io/api/random?count={questions_num}')  # Выполнение запроса к API викторин
        if response.status_code == 200:  # Проверка успешности запроса
            data = response.json()  # Извлечение данных из ответа

            bulk_objects = []  # Список для хранения объектов модели для пакетной вставки в базу данных
            for question in data:
                existing_question = Baza.query.filter_by(question=question['question']).first()  # Проверка наличия такого же вопроса в базе данных
                if existing_question:
                    while existing_question:  # Если вопрос уже существует, выполняется дополнительный запрос для получения уникального вопроса
                        response = requests.get(f'https://jservice.io/api/random?count=1')
                        if response.status_code == 200:
                            question_data = response.json()[0]
                            existing_question = Baza.query.filter_by(question=question_data['question']).first()
                        else:
                            return {'message': 'Failed to fetch questions'}, 500

                created_at = datetime.now()  # Установка текущей даты и времени в качестве даты создания вопроса

                instance = Baza(id_question=question['id'], question=question['question'],
                                answer=question['answer'], created_at=created_at)  # Создание экземпляра модели с полученными данными
                bulk_objects.append(instance)  # Добавление экземпляра модели в список

            db.session.bulk_save_objects(bulk_objects)  # Пакетное сохранение объектов модели в базу данных
            db.session.commit()  # Фиксация изменений в базе данных

            return data, 201  # Возврат данных в качестве ответа на запрос

        return {'message': 'Failed to fetch questions'}, 500  # Обработка ошибки при получении вопросов

# Регистрация ресурса Main с маршрутом и параметром id_
api.add_resource(Main, "/query-example/<int:id_>")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=3000, host="127.0.0.1")




