#!/usr/bin/env python3
from flask import Flask, render_template, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    
    # Enable CORS
    CORS(app)
    
    # Initialize database connection
    from app.models.database import Neo4jDB
    app.db = Neo4jDB()
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.course import course_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(course_bp, url_prefix='/course')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html')
    
    @app.route('/graph')
    def graph_view():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('graph.html')
    
    @app.route('/leaderboard')
    def leaderboard():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('leaderboard.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Initialize sample data
    print("🚀 Initializing MIT Statistics course data...")
    app.db.create_sample_course()
    
    print("🌟 Starting Neo4j Learning Platform...")
    app.run(host='0.0.0.0', port=5000, debug=True)
