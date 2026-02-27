"""
Flask application for Skill-Based Internship & Project Matching Platform
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from database import get_db, init_db, DATABASE_PATH
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE_PATH):
    init_db()


# ================== DATABASE HELPER FUNCTIONS ==================

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary."""
    if row is None:
        return None
    return dict(row)


# ================== CANDIDATE OPERATIONS ==================

def add_candidate(name, email, experience_months, projects_completed, certifications, availability, skills):
    """
    Add a new candidate to the database.
    
    Args:
        name: Candidate name
        email: Candidate email
        experience_months: Months of experience
        projects_completed: Number of projects completed
        certifications: Number of certifications
        availability: Full-time or Part-time
        skills: List of dicts with 'skill_name' and 'skill_level'
    
    Returns:
        Candidate ID
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Insert candidate
        cursor.execute('''
            INSERT INTO candidates 
            (name, email, experience_months, projects_completed, certifications, availability)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, experience_months, projects_completed, certifications, availability))
        
        candidate_id = cursor.lastrowid
        
        # Insert skills
        for skill in skills:
            if skill['skill_name'].strip():  # Only add non-empty skills
                cursor.execute('''
                    INSERT INTO candidate_skills 
                    (candidate_id, skill_name, skill_level)
                    VALUES (?, ?, ?)
                ''', (candidate_id, skill['skill_name'], skill['skill_level']))
        
        conn.commit()
        return candidate_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_candidate(candidate_id):
    """Get candidate details by ID."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
    candidate = dict_from_row(cursor.fetchone())
    
    if candidate:
        cursor.execute(
            'SELECT skill_name, skill_level FROM candidate_skills WHERE candidate_id = ?',
            (candidate_id,)
        )
        candidate['skills'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return candidate


def get_all_candidates():
    """Get all candidates."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM candidates ORDER BY created_at DESC')
    candidates = [dict_from_row(row) for row in cursor.fetchall()]
    
    for candidate in candidates:
        cursor.execute(
            'SELECT skill_name, skill_level FROM candidate_skills WHERE candidate_id = ?',
            (candidate['id'],)
        )
        candidate['skills'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return candidates


# ================== PROJECT OPERATIONS ==================

def add_project(company_name, role_title, duration, stipend_amount, required_skills):
    """
    Add a new internship project posting.
    
    Args:
        company_name: Company name
        role_title: Role/Position title
        duration: Duration (e.g., "3 months")
        stipend_amount: Stipend amount (0 if not offered)
        required_skills: List of dicts with 'skill_name', 'weight', 'minimum_level'
    
    Returns:
        Project ID
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Insert project
        cursor.execute('''
            INSERT INTO projects 
            (company_name, role_title, duration, stipend_amount)
            VALUES (?, ?, ?, ?)
        ''', (company_name, role_title, duration, stipend_amount))
        
        project_id = cursor.lastrowid
        
        # Insert required skills
        for skill in required_skills:
            if skill['skill_name'].strip():  # Only add non-empty skills
                cursor.execute('''
                    INSERT INTO project_skills 
                    (project_id, skill_name, weight, minimum_level)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, skill['skill_name'], skill['weight'], skill['minimum_level']))
        
        conn.commit()
        return project_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_project(project_id):
    """Get project details by ID."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = dict_from_row(cursor.fetchone())
    
    if project:
        cursor.execute(
            'SELECT skill_name, weight, minimum_level FROM project_skills WHERE project_id = ?',
            (project_id,)
        )
        project['required_skills'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return project


def get_all_projects():
    """Get all projects."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = [dict_from_row(row) for row in cursor.fetchall()]
    
    for project in projects:
        cursor.execute(
            'SELECT skill_name, weight, minimum_level FROM project_skills WHERE project_id = ?',
            (project['id'],)
        )
        project['required_skills'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return projects


# ================== MATCHING ALGORITHM ==================

def calculate_match_score(candidate, project):
    """
    Calculate weighted competency score for a candidate against a project.
    
    Algorithm:
    - For each required skill:
        - If candidate has skill: score += (candidate_level × weight)
        - If candidate level < minimum required: apply penalty
        - If skill not present: score += 0
    - Final score = total_score / total_weights × 100
    
    Args:
        candidate: Candidate dict with skills
        project: Project dict with required_skills
    
    Returns:
        Dict with match_score, strong_matches, partial_matches, missing_skills, explanation
    """
    
    # Create a map of candidate skills for quick lookup
    candidate_skills_map = {
        skill['skill_name'].lower(): skill['skill_level']
        for skill in candidate.get('skills', [])
    }
    
    total_score = 0
    total_weights = 0
    strong_matches = []
    partial_matches = []
    missing_skills = []
    
    # Calculate score for each required skill
    for required_skill in project.get('required_skills', []):
        skill_name = required_skill['skill_name'].lower()
        weight = float(required_skill['weight'])
        minimum_level = required_skill['minimum_level']
        total_weights += weight
        
        if skill_name in candidate_skills_map:
            candidate_level = candidate_skills_map[skill_name]
            
            if candidate_level >= minimum_level:
                # Strong match
                score_contribution = candidate_level * weight
                total_score += score_contribution
                strong_matches.append({
                    'skill': required_skill['skill_name'],
                    'candidate_level': candidate_level,
                    'required_level': minimum_level
                })
            else:
                # Partial match (skill present but below required level)
                score_contribution = (candidate_level / minimum_level) * weight * 0.5
                total_score += score_contribution
                partial_matches.append({
                    'skill': required_skill['skill_name'],
                    'candidate_level': candidate_level,
                    'required_level': minimum_level
                })
        else:
            # Missing skill
            missing_skills.append({
                'skill': required_skill['skill_name'],
                'required_level': minimum_level
            })
    
    # Calculate final percentage score
    if total_weights > 0:
        match_score = (total_score / total_weights) * 100
    else:
        match_score = 0
    
    # Generate explanation
    explanation = generate_explanation(
        candidate, strong_matches, partial_matches, missing_skills, match_score
    )
    
    return {
        'match_score': round(match_score, 2),
        'strong_matches': strong_matches,
        'partial_matches': partial_matches,
        'missing_skills': missing_skills,
        'explanation': explanation
    }


def generate_explanation(candidate, strong_matches, partial_matches, missing_skills, score):
    """Generate a human-readable explanation of the match."""
    
    strong_skills = [s['skill'] for s in strong_matches]
    partial_skills = [s['skill'] for s in partial_matches]
    missing = [s['skill'] for s in missing_skills]
    
    explanation_parts = []
    
    # Build explanation
    if score >= 85:
        explanation_parts.append("Excellent fit!")
    elif score >= 70:
        explanation_parts.append("Strong candidate.")
    elif score >= 50:
        explanation_parts.append("Moderate fit.")
    else:
        explanation_parts.append("May require additional training.")
    
    if strong_skills:
        explanation_parts.append(
            f"Strong skills: {', '.join(strong_skills[:3])}."
        )
    
    if partial_skills:
        explanation_parts.append(
            f"Has some experience with {', '.join(partial_skills[:2])} but below required level."
        )
    
    if missing_skills:
        if len(missing_skills) <= 2:
            explanation_parts.append(
                f"Missing key skills: {', '.join(missing)}."
            )
        else:
            explanation_parts.append(
                f"Missing {len(missing_skills)} required skills. Training may be needed."
            )
    
    # Add experience note
    experience = candidate.get('experience_months', 0)
    if experience >= 12:
        explanation_parts.append(f"Has {experience} months of relevant experience.")
    
    return " ".join(explanation_parts)


def match_candidates_to_project(project_id):
    """
    Match all candidates to a specific project and rank them.
    
    Returns:
        List of candidates ranked by match score (descending)
    """
    project = get_project(project_id)
    if not project:
        return []
    
    candidates = get_all_candidates()
    results = []
    
    # Calculate match score for each candidate
    for candidate in candidates:
        match_data = calculate_match_score(candidate, project)
        result = {
            'candidate_id': candidate['id'],
            'candidate_name': candidate['name'],
            'candidate_email': candidate['email'],
            'availability': candidate['availability'],
            'experience_months': candidate['experience_months'],
            'projects_completed': candidate['projects_completed'],
            'certifications': candidate['certifications'],
            **match_data
        }
        results.append(result)
    
    # Sort by match score descending
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Save results to cache
    conn = get_db()
    cursor = conn.cursor()
    for idx, result in enumerate(results):
        cursor.execute('''
            INSERT INTO match_results 
            (project_id, candidate_id, match_score, strong_matches, 
             partial_matches, missing_skills, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            result['candidate_id'],
            result['match_score'],
            str(result['strong_matches']),
            str(result['partial_matches']),
            str(result['missing_skills']),
            result['explanation']
        ))
    conn.commit()
    conn.close()
    
    return results


# ================== FLASK ROUTES ==================

@app.route('/')
def index():
    """Home page with candidate and project sections."""
    return render_template('index.html')


@app.route('/candidate_form')
def candidate_form():
    """Candidate registration form."""
    return render_template('candidate_form.html')


@app.route('/project_form')
def project_form():
    """Project posting form."""
    return render_template('project_form.html')


@app.route('/add_candidate', methods=['POST'])
def add_candidate_route():
    """API endpoint to add a new candidate."""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Name and email are required'}), 400
        
        if not data.get('skills') or len(data['skills']) == 0:
            return jsonify({'error': 'At least one skill is required'}), 400
        
        candidate_id = add_candidate(
            name=data['name'],
            email=data['email'],
            experience_months=int(data.get('experience_months', 0)),
            projects_completed=int(data.get('projects_completed', 0)),
            certifications=int(data.get('certifications', 0)),
            availability=data['availability'],
            skills=data['skills']
        )
        
        return jsonify({
            'success': True,
            'message': 'Candidate registered successfully',
            'candidate_id': candidate_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/add_project', methods=['POST'])
def add_project_route():
    """API endpoint to add a new project."""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('company_name') or not data.get('role_title'):
            return jsonify({'error': 'Company name and role title are required'}), 400
        
        if not data.get('required_skills') or len(data['required_skills']) == 0:
            return jsonify({'error': 'At least one required skill is needed'}), 400
        
        stipend = float(data.get('stipend_amount', 0)) if data.get('stipend_offered') else 0
        
        project_id = add_project(
            company_name=data['company_name'],
            role_title=data['role_title'],
            duration=data['duration'],
            stipend_amount=stipend,
            required_skills=data['required_skills']
        )
        
        return jsonify({
            'success': True,
            'message': 'Project posted successfully',
            'project_id': project_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/match/<int:project_id>', methods=['GET'])
def match_route(project_id):
    """API endpoint to get candidate matches for a project."""
    try:
        project = get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        results = match_candidates_to_project(project_id)
        
        return jsonify({
            'success': True,
            'project': {
                'id': project['id'],
                'company_name': project['company_name'],
                'role_title': project['role_title'],
                'duration': project['duration'],
                'stipend_amount': project['stipend_amount']
            },
            'total_candidates': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/projects', methods=['GET'])
def get_projects_route():
    """API endpoint to get all projects."""
    try:
        projects = get_all_projects()
        return jsonify({
            'success': True,
            'projects': projects
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/candidates', methods=['GET'])
def get_candidates_route():
    """API endpoint to get all candidates."""
    try:
        candidates = get_all_candidates()
        return jsonify({
            'success': True,
            'candidates': candidates
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


# ================== ERROR HANDLERS ==================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)