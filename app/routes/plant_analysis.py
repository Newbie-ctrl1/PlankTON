from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import PlantAnalysis
from app import db
from app.services.plantid_service import PlantIdService
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('plant_analysis', __name__, url_prefix='/api/plant')

# Common plant names dictionary (Latin -> Indonesian, English)
PLANT_NAMES = {
    'Solanum lycopersicum': {'id': 'Tomat', 'en': 'Tomato'},
    'Capsicum annuum': {'id': 'Cabai/Paprika', 'en': 'Bell Pepper/Chili'},
    'Cucumis sativus': {'id': 'Mentimun', 'en': 'Cucumber'},
    'Solanum melongena': {'id': 'Terong', 'en': 'Eggplant'},
    'Musa acuminata': {'id': 'Pisang', 'en': 'Banana'},
    'Manihot esculenta': {'id': 'Singkong', 'en': 'Cassava'},
    'Solanum tuberosum': {'id': 'Kentang', 'en': 'Potato'},
    'Zea mays': {'id': 'Jagung', 'en': 'Corn'},
    'Triticum aestivum': {'id': 'Gandum', 'en': 'Wheat'},
    'Oryza sativa': {'id': 'Padi/Beras', 'en': 'Rice'},
    'Ipomoea batatas': {'id': 'Ubi Jalar', 'en': 'Sweet Potato'},
    'Daucus carota': {'id': 'Wortel', 'en': 'Carrot'},
    'Lactuca sativa': {'id': 'Selada/Lettuce', 'en': 'Lettuce'},
    'Allium cepa': {'id': 'Bawang Merah', 'en': 'Red Onion'},
    'Allium sativum': {'id': 'Bawang Putih', 'en': 'Garlic'},
    'Lycopersicon esculentum': {'id': 'Tomat', 'en': 'Tomato'},  # Alternative name
    'Carica papaya': {'id': 'Pepaya', 'en': 'Papaya'},
    'Mangifera indica': {'id': 'Mangga', 'en': 'Mango'},
    'Artocarpus heterophyllus': {'id': 'Nangka', 'en': 'Jackfruit'},
    'Cucurbita pepo': {'id': 'Labu/Zucchini', 'en': 'Squash/Zucchini'},
    'Phaseolus vulgaris': {'id': 'Kacang Panjang/Buncis', 'en': 'Green Beans'},
    'Brassica oleracea': {'id': 'Kubis/Kol', 'en': 'Cabbage'},
    'Brassica rapa': {'id': 'Sawi', 'en': 'Mustard Green'},
    'Amaranthus': {'id': 'Bayam', 'en': 'Amaranth'},
    'Spinacia oleracea': {'id': 'Bayam Darat', 'en': 'Spinach'},
}

def get_plant_translation(scientific_name):
    """Get Indonesian and English names for a plant"""
    if scientific_name in PLANT_NAMES:
        return PLANT_NAMES[scientific_name]
    # Try to find partial match
    for key, value in PLANT_NAMES.items():
        if key.lower() in scientific_name.lower() or scientific_name.lower() in key.lower():
            return value
    # Return original name if not found
    return {'id': scientific_name, 'en': scientific_name}

# Lazy load plantid_service
plantid_service = None
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')

def get_plantid_service():
    global plantid_service
    if plantid_service is None:
        plantid_service = PlantIdService(api_key=os.getenv('PLANTID_API_KEY'))
    return plantid_service

def generate_health_recommendations(plant_name, diseases, pests):
    """Generate AI recommendations untuk health issues"""
    from app.services.groq_service import GroqService
    
    health_issues = []
    
    for disease in diseases[:3]:
        health_issues.append(f"Penyakit: {disease['name']} (confidence: {disease['probability']*100:.0f}%)")
    
    for pest in pests[:3]:
        health_issues.append(f"Hama: {pest['name']} (confidence: {pest['probability']*100:.0f}%)")
    
    issues_text = '\n'.join(health_issues)
    
    prompt = f"""Berikan saran penanganan lengkap untuk {plant_name} yang mengalami masalah berikut:

{issues_text}

Berikan dalam format:
1. Diagnosis singkat (2-3 baris untuk setiap masalah)
2. 3-4 langkah penanganan praktis (dengan tabel: Langkah | Aksi | Cara Praktis)
3. Pencegahan di masa depan (8-10 poin)

Gunakan bahasa Indonesia yang sederhana dan praktis untuk petani."""
    
    try:
        groq_service = GroqService(api_key=os.getenv('GROQ_API_KEY'))
        response = groq_service.get_plant_response(prompt)
        return response
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return None

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/analyze', methods=['POST'])
@login_required
def analyze_plant():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Tidak ada file gambar'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'File tidak dipilih'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Format file tidak didukung'}), 400
        
        # Check if Plant.id API key is configured
        api_key = os.getenv('PLANTID_API_KEY', '').strip()
        if not api_key or api_key == 'your_plantid_api_key_here':
            return jsonify({
                'error': 'Plant.id API key belum dikonfigurasi',
                'message': 'Silakan set PLANTID_API_KEY di file .env dan restart Flask'
            }), 503
        
        # Save file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = secure_filename(timestamp + file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Analyze with Plant.id API
        service = get_plantid_service()
        result = service.identify_plant(filepath)
        
        print(f"DEBUG: Plant analysis result: {result}")
        
        if not result:
            return jsonify({'error': 'Gagal menganalisis tanaman'}), 500
        
        # Save to database dengan user_id
        plant_name = result.get('name', 'Tidak diketahui')
        confidence = result.get('confidence', 0)
        
        # Get plant name translation
        plant_translation = get_plant_translation(plant_name)
        plant_id_name = plant_translation.get('id', plant_name)
        plant_en_name = plant_translation.get('en', plant_name)
        
        # Generate AI recommendations
        ai_recommendations = None
        health_data = result.get('health', {})
        diseases = health_data.get('diseases', {}).get('suggestions', [])
        pests = health_data.get('pests', {}).get('suggestions', [])
        
        if diseases or pests:
            try:
                ai_recommendations = generate_health_recommendations(plant_id_name, diseases, pests)
            except Exception as e:
                print(f"Warning: Could not generate recommendations: {e}")
                ai_recommendations = None
        
        analysis = PlantAnalysis(
            user_id=current_user.id,
            image_filename=filename,
            plant_name=plant_name,
            confidence=confidence,
            analysis_result=result,
            ai_recommendations=ai_recommendations
        )
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'id': analysis.id,
            'plant_name': plant_name,
            'plant_name_id': plant_id_name,
            'plant_name_en': plant_en_name,
            'confidence': confidence,
            'image_url': f'/static/uploads/{filename}',
            'health': result.get('health', {}),
            'analysis_result': result,
            'ai_recommendations': ai_recommendations,
            'created_at': analysis.created_at.isoformat()
        }), 201
    
    except Exception as e:
        print(f"PLANT ANALYSIS ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/health-advice', methods=['POST'])
@login_required
def get_health_advice():
    """Get AI-powered health advice for detected diseases/pests"""
    try:
        data = request.get_json()
        plant_name = data.get('plant_name', '')
        diseases = data.get('diseases', [])
        pests = data.get('pests', [])
        
        if not plant_name or (not diseases and not pests):
            return jsonify({'error': 'Invalid request'}), 400
        
        # Build prompt for Groq
        health_issues = []
        
        for disease in diseases[:3]:  # Top 3
            health_issues.append(f"Penyakit: {disease['name']} (confidence: {disease['probability']*100:.0f}%)")
        
        for pest in pests[:3]:  # Top 3
            health_issues.append(f"Hama: {pest['name']} (confidence: {pest['probability']*100:.0f}%)")
        
        issues_text = '\n'.join(health_issues)
        
        prompt = f"""Berikan saran penanganan singkat untuk {plant_name} yang mengalami masalah berikut:

{issues_text}

Berikan:
1. Diagnosis singkat
2. 3-4 langkah penanganan praktis
3. Pencegahan di masa depan

Gunakan bahasa Indonesia yang sederhana dan praktis untuk petani."""
        
        # Get Groq service
        from app.services.groq_service import GroqService
        groq_service = GroqService(api_key=os.getenv('GROQ_API_KEY'))
        response = groq_service.get_plant_response(prompt)
        
        return jsonify({
            'advice': response,
            'plant': plant_name,
            'issues_count': len(health_issues)
        }), 200
    
    except Exception as e:
        print(f"HEALTH ADVICE ERROR: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@login_required
def get_analysis_history():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = PlantAnalysis.query.filter_by(user_id=current_user.id).order_by(PlantAnalysis.created_at.desc()).paginate(
            page=page, per_page=per_page
        )
        
        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'data': [
                {
                    **analysis.to_dict(),
                    'image_url': f'/static/uploads/{analysis.image_filename}'
                }
                for analysis in pagination.items
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history/<int:analysis_id>', methods=['DELETE'])
@login_required
def delete_analysis(analysis_id):
    try:
        analysis = PlantAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
        
        # Delete image file
        filepath = os.path.join(UPLOAD_FOLDER, analysis.image_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        db.session.delete(analysis)
        db.session.commit()
        
        return jsonify({'message': 'Analisis dihapus'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history/clear', methods=['POST'])
@login_required
def clear_analysis_history():
    """Clear all plant analysis history for current user"""
    try:
        # Get all analyses for current user
        analyses = PlantAnalysis.query.filter_by(user_id=current_user.id).all()
        
        # Delete all image files
        for analysis in analyses:
            filepath = os.path.join(UPLOAD_FOLDER, analysis.image_filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Warning: Could not delete file {filepath}: {e}")
        
        # Delete all records
        PlantAnalysis.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({'message': 'Semua riwayat analisis dihapus'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
