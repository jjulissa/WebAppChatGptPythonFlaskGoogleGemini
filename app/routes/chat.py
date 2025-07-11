# app/routes/chat.py 

from flask import Blueprint, request, jsonify 
from flask_jwt_extended import jwt_required, get_jwt_identity  
from marshmallow import Schema, fields, ValidationError
import google.generativeai as genai 
from app.models import db, ChatMessage 
import os

# Configura la API Key globalmente
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Crea el modelo Gemini SOLO UNA VEZ y SIN api_key como argumento
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

chat_bp = Blueprint('chat', __name__)

class ChatSchema(Schema):
    content = fields.Str(required=True)

@chat_bp.route('/chat/send', methods=['POST'])
@jwt_required()
def send_message():
    schema = ChatSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user_input = data['content']
    user_id = get_jwt_identity()

    # Guarda el mensaje del usuario
    user_message = ChatMessage(
        user_id=user_id,
        role='user',
        content=user_input
    )
    db.session.add(user_message)
    db.session.commit()

    try:
        response = gemini_model.generate_content(
            user_input,
            generation_config={"timeout": 10}
        )
        answer = response.text

        # Guarda la respuesta del asistente
        assistant_message = ChatMessage(
            user_id=user_id,
            role='assistant',
            content=answer
        )
        db.session.add(assistant_message)
        db.session.commit()

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": "Error comunicando con Gemini API"}), 502 
    

@chat_bp.route('/chat/history', methods=['GET'])
@jwt_required()
def chat_history(): 
    user_id = get_jwt_identity()
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.timestamp).all()
    history = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]
    return jsonify({"history": history})



