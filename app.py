from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import string
import os

# Убедимся, что все ресурсы NLTK загружены
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    answer = db.Column(db.String(1000))
    variations = db.Column(db.JSON)

def preprocess_text(text):
    try:
        tokens = nltk.word_tokenize(text.lower())
        tokens = [ps.stem(t) for t in tokens if t not in stop_words and t not in string.punctuation]
        return set(tokens)
    except Exception as e:
        print(f"Ошибка при обработке текста: {e}")
        return set()

def find_best_answer(question):
    processed = preprocess_text(question)
    
    questions = Question.query.all()
    best_match = None
    max_score = 0
    
    for q in questions:
        q_text_processed = preprocess_text(q.text)
        score = len(processed.intersection(q_text_processed))
        
        if q.variations:
            for variation in q.variations:
                var_processed = preprocess_text(variation)
                var_score = len(processed.intersection(var_processed))
                if var_score > score:
                    score = var_score
        
        if score > max_score:
            max_score = score
            best_match = q
    
    return best_match.answer if best_match and max_score >= 2 else None

@app.route('/api/chat', methods=['POST'])
def handle_message():
    data = request.json
    user_message = data['message'].strip().lower()
    
    if any(word in user_message for word in ['привет', 'здравствуйте', 'добрый день']):
        return jsonify({
            'answer': 'Здравствуйте! Я виртуальный помощник Политех Петра. Задайте вопрос о поступлении, факультетах или студенческой жизни.',
            'status': 'bot'
        })
    
    answer = find_best_answer(user_message)
    
    if answer:
        return jsonify({
            'answer': answer,
            'status': 'bot'
        })
    else:
        return jsonify({
            'answer': 'Извините, я не нашел ответа на ваш вопрос. 😕\n\nВы можете:\n1. Уточнить формулировку\n2. Позвонить в приемную комиссию: 8 (812) 775-05-30\n3. Написать на email: abitur@spbstu.ru',
            'status': 'bot'
        })

# Инициализация базы данных
with app.app_context():
    db.create_all()
    
    if not Question.query.first():
        questions = [
            {
                "text": "Какие факультеты есть в университете?",
                "answer": "В Политех Петра представлены:\n\n🔹 Гумманитарный институт (ЛИНГВИСТИКА, ИЗДАТЕЛЬСКОЕ ДЕЛО, РЕКЛАМА И СВЯЗИ С ОБЩЕСТВЕННОСТЬЮ, ПСИХОЛОГО-ПЕДАГОГИЧЕСКОЕ ОБРАЗОВАНИЕ, ЮРИСПРУДЕНЦИЯ, ЗАРУБЕЖНОЕ РЕГИОНОВЕДЕНИЕ )\n🔹 Инженерно-строительный институт (Дизайн архитектурной среды, Строительство, Техносферная безопасность, Дизайн, Дизайн архитектурной среды, Градостроительство,  )\n🔹 Институт биомедицинских систем и биотехнологий (Биоинженерия и биоинформатика, Биотехнические системы и технологии, Биотехнология, Продукты питания животного происхождения, Технология продукции и организация общественного питания)\n🔹Институт машиностроения, материалов и транспорта  (Машиностроение, Технологические машины и оборудование, Автоматизация технологических процессов и производств, Конструкторско-технологическое обеспечение машиностроительных производств, Мехатроника и робототехника, Материаловедение и технологии материалов, Металлургия, Технология транспортных процессов, Управление качеством, Инноватика, Нанотехнологии и микросистемная техника, Технология художественной обработки материалов, Машиностроение)\n и др. \n\nПодробнее: https://www.spbstu.ru/education/management-structure/institutions/",
                "variations": ["Какие есть направления?", "Перечислите факультеты"]
            },
            {
                "text": "Какие проходные баллы?",
                "answer": "Проходные баллы 2024 года:\n\n💻 Компьютерные науки: 245\n⚙️ Инженерные направления: 210",
                "variations": ["Сколько баллов нужно?", "Минимальные баллы ЕГЭ"]
            }
        ]
        
        for q in questions:
            new_question = Question(
                text=q['text'],
                answer=q['answer'],
                variations=q['variations']
            )
            db.session.add(new_question)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)