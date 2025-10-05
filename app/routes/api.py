from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
from app.models.course import Course
from app.models.user import User
from app.models.ai_engine import AILearningEngine
from app.models.gamification import GamificationEngine
from app.models.collaboration import CollaborationEngine

api_bp = Blueprint('api', __name__)

@api_bp.route('/graph')
def get_graph():
    try:
        from flask import current_app
        graph_data = current_app.db.get_course_graph()
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/concept/<concept_id>')
def get_concept(concept_id):
    try:
        from flask import current_app
        course_model = Course(current_app.db)
        concept = course_model.get_concept_details(concept_id)
        
        if not concept:
            return jsonify({'error': 'Concept not found'}), 404
        
        return jsonify(concept)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/progress')
def get_user_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        user_model = User(current_app.db)
        progress = user_model.get_user_progress(session['user_id'])
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/concept/<concept_id>/complete', methods=['POST'])
def mark_complete(concept_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        user_model = User(current_app.db)
        user_model.mark_concept_complete(session['user_id'], concept_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/learning-path')
def get_learning_path():
    try:
        from flask import current_app
        course_model = Course(current_app.db)
        user_id = session.get('user_id')
        path = course_model.get_learning_path(user_id)
        return jsonify(path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AI-Powered Endpoints
@api_bp.route('/ai-recommendations')
def get_ai_recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        ai_engine = AILearningEngine(current_app.db)
        recommendations = ai_engine.analyze_learning_pattern(session['user_id'])
        
        # Ensure all values are properly formatted
        if 'next_optimal_study_time' in recommendations and isinstance(recommendations['next_optimal_study_time'], datetime):
            recommendations['next_optimal_study_time'] = recommendations['next_optimal_study_time'].isoformat()
        
        return jsonify(recommendations)
    except Exception as e:
        print(f"AI recommendations error: {e}")  # Debug logging
        # Return default recommendations instead of error
        return jsonify({
            'learning_style': 'visual',
            'retention_score': 0.7,
            'optimal_pace': 'moderate',
            'difficulty_preference': 'progressive',
            'avg_attempts': 1.5,
            'total_concepts_completed': 0,
            'confidence_level': 50,
            'recommended_session_length': 30,
            'next_optimal_study_time': (datetime.now() + timedelta(hours=24)).isoformat()
        })

@api_bp.route('/adaptive-learning-path')
def get_adaptive_learning_path():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        ai_engine = AILearningEngine(current_app.db)
        path = ai_engine.generate_adaptive_path(session['user_id'])
        return jsonify({'concepts': path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/personalized-content/<concept_id>')
def get_personalized_content(concept_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        ai_engine = AILearningEngine(current_app.db)
        content = ai_engine.generate_personalized_content(concept_id, session['user_id'])
        return jsonify(content)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Gamification Endpoints
@api_bp.route('/user-stats')
def get_user_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        gamification = GamificationEngine(current_app.db)
        stats = gamification.get_user_stats(session['user_id'])
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/achievements')
def get_achievements():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        gamification = GamificationEngine(current_app.db)
        achievements = gamification.check_achievements(session['user_id'])
        return jsonify({'recent': achievements})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/skill-trees')
def get_skill_trees():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        gamification = GamificationEngine(current_app.db)
        skill_trees = gamification.get_skill_tree_progress(session['user_id'])
        return jsonify(skill_trees)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/leaderboard')
def get_leaderboard():
    try:
        from flask import current_app
        gamification = GamificationEngine(current_app.db)
        timeframe = request.args.get('timeframe', 'all_time')
        leaderboard = gamification.get_leaderboard(timeframe)
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Collaboration Endpoints
@api_bp.route('/study-groups')
def get_study_groups():
    try:
        from flask import current_app
        collaboration = CollaborationEngine(current_app.db)
        user_id = session.get('user_id')
        groups = collaboration.get_study_groups(user_id)
        return jsonify(groups)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/create-study-group', methods=['POST'])
def create_study_group():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        from flask import current_app
        collaboration = CollaborationEngine(current_app.db)
        
        group_id = collaboration.create_study_group(
            session['user_id'],
            data['name'],
            data['description'],
            data.get('max_members', 10),
            data.get('is_public', True)
        )
        
        return jsonify({'group_id': group_id, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/join-study-group/<group_id>', methods=['POST'])
def join_study_group(group_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        collaboration = CollaborationEngine(current_app.db)
        success = collaboration.join_study_group(group_id, session['user_id'])
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/collaborative-sessions/<group_id>')
def get_collaborative_sessions(group_id):
    try:
        from flask import current_app
        collaboration = CollaborationEngine(current_app.db)
        sessions = collaboration.get_active_sessions(group_id)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/start-collaborative-session', methods=['POST'])
def start_collaborative_session():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        from flask import current_app
        collaboration = CollaborationEngine(current_app.db)
        
        session_info = collaboration.start_collaborative_session(
            data['group_id'],
            data['concept_id'],
            session['user_id']
        )
        
        return jsonify(session_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Advanced Analytics
@api_bp.route('/learning-analytics')
def get_learning_analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        ai_engine = AILearningEngine(current_app.db)
        analytics = ai_engine.analyze_learning_pattern(session['user_id'])
        
        # Add more detailed analytics
        analytics['weekly_progress'] = [1, 2, 1, 3, 2, 1, 4]  # Mock data
        analytics['mastery_breakdown'] = {'Beginner': 5, 'Intermediate': 3, 'Advanced': 1}
        analytics['time_spent_daily'] = [30, 45, 20, 60, 35, 25, 50]  # Minutes
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ai-session')
def get_ai_session():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        ai_engine = AILearningEngine(current_app.db)
        
        # Get personalized session
        profile = ai_engine.analyze_learning_pattern(session['user_id'])
        path = ai_engine.generate_adaptive_path(session['user_id'])
        
        if path:
            recommended_concept = path[0]
            content = ai_engine.generate_personalized_content(
                recommended_concept['id'], 
                session['user_id']
            )
            
            return jsonify({
                'learning_style': profile['learning_style'],
                'recommended_concept': recommended_concept,
                'study_tips': content.get('study_tips', []),
                'session_length': profile['recommended_session_length']
            })
        else:
            return jsonify({'error': 'No recommendations available'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/regenerate-path', methods=['POST'])
def regenerate_path():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        ai_engine = AILearningEngine(current_app.db)
        path = ai_engine.generate_adaptive_path(session['user_id'])
        return jsonify({'success': True, 'concepts': path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
