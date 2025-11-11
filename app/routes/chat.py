from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import ChatHistory
from app import db
from app.services.groq_service import GroqService
import os

bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Lazy load groq_service
groq_service = None

def get_groq_service():
    global groq_service
    if groq_service is None:
        groq_service = GroqService(api_key=os.getenv('GROQ_API_KEY'))
    return groq_service

@bp.route('/send', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        plant_topic = data.get('plant_topic', 'tanaman umum')
        
        if not user_message:
            return jsonify({'error': 'Pesan tidak boleh kosong'}), 400
        
        # Get AI response from Groq
        service = get_groq_service()
        ai_response = service.get_plant_response(user_message, plant_topic)
        
        # Save to database dengan user_id
        chat_entry = ChatHistory(
            user_id=current_user.id,
            user_message=user_message,
            ai_response=ai_response,
            plant_topic=plant_topic
        )
        db.session.add(chat_entry)
        db.session.commit()
        
        return jsonify({
            'id': chat_entry.id,
            'user_message': user_message,
            'ai_response': ai_response,
            'plant_topic': plant_topic,
            'created_at': chat_entry.created_at.isoformat()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@login_required
def get_history():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at.desc()).paginate(
            page=page, per_page=per_page
        )
        
        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'data': [chat.to_dict() for chat in pagination.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    try:
        chat = ChatHistory.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
        db.session.delete(chat)
        db.session.commit()
        
        return jsonify({'message': 'Chat dihapus'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history/clear', methods=['POST'])
@login_required
def clear_history():
    try:
        ChatHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({'message': 'Riwayat chat dihapus'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
