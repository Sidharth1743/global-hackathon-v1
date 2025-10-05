from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models.course import Course
from app.models.user import User

course_bp = Blueprint('course', __name__)

@course_bp.route('/list')
def course_list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        from flask import current_app
        course_model = Course(current_app.db)
        concepts = course_model.get_all_concepts()
        return render_template('course/list.html', concepts=concepts)
    except Exception as e:
        flash(f'Error loading courses: {str(e)}', 'error')
        return redirect(url_for('index'))

@course_bp.route('/concept/<concept_id>')
def concept_detail(concept_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        from flask import current_app
        course_model = Course(current_app.db)
        
        concept = course_model.get_concept_details(concept_id)
        if not concept:
            flash('Concept not found', 'error')
            return redirect(url_for('course.course_list'))
        
        prerequisites = course_model.get_prerequisites(concept_id)
        next_concepts = course_model.get_next_concepts(concept_id)
        
        return render_template('course/concept.html', 
                             concept=concept,
                             prerequisites=prerequisites, 
                             next_concepts=next_concepts)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('course.course_list'))

@course_bp.route('/concept/<concept_id>/complete', methods=['POST'])
def complete_concept(concept_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import current_app
        user_model = User(current_app.db)
        user_model.mark_concept_complete(session['user_id'], concept_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@course_bp.route('/graph')
def course_graph():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('course/graph.html')
