"""
AI-Powered Learning Engine
Advanced algorithms for personalized learning optimization
"""
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np

class AILearningEngine:
    def __init__(self, db):
        self.db = db
        self.learning_styles = ['visual', 'auditory', 'kinesthetic', 'reading']
        self.difficulty_weights = {'Beginner': 1.0, 'Intermediate': 1.5, 'Advanced': 2.0}
        
    def analyze_learning_pattern(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's learning patterns using AI algorithms"""
        
        # Get user's learning history
        history = self.db.execute_query('''
            MATCH (u:User {id: $user_id})-[r:COMPLETED]->(c:Concept)
            RETURN c.id as concept_id, c.difficulty as difficulty, 
                   r.completion_time as time, r.attempts as attempts,
                   r.timestamp as timestamp
            ORDER BY r.timestamp DESC
        ''', {'user_id': user_id})
        
        if not history:
            return self._default_learning_profile()
        
        # Calculate learning metrics
        total_concepts = len(history)
        avg_attempts = sum(h.get('attempts', 1) or 1 for h in history) / total_concepts if total_concepts > 0 else 1
        
        # Determine learning style based on performance patterns
        learning_style = self._detect_learning_style(history)
        
        # Calculate knowledge retention score
        retention_score = self._calculate_retention_score(history)
        
        # Predict optimal learning pace
        optimal_pace = self._predict_learning_pace(history)
        
        # Generate difficulty preference
        difficulty_preference = self._analyze_difficulty_preference(history)
        
        return {
            'learning_style': learning_style,
            'retention_score': retention_score,
            'optimal_pace': optimal_pace,
            'difficulty_preference': difficulty_preference,
            'avg_attempts': avg_attempts,
            'total_concepts_completed': total_concepts,
            'confidence_level': min(retention_score * 100, 95),
            'recommended_session_length': self._recommend_session_length(history),
            'next_optimal_study_time': self._predict_next_study_time(history)
        }
    
    def generate_adaptive_path(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate AI-optimized learning path based on user's profile"""
        
        profile = self.analyze_learning_pattern(user_id)
        
        # Get all available concepts
        concepts = self.db.execute_query('''
            MATCH (c:Concept)
            WHERE c.name IS NOT NULL
            OPTIONAL MATCH (u:User {id: $user_id})-[comp:COMPLETED]->(c)
            RETURN c.id as id, c.name as name, c.difficulty as difficulty,
                   comp IS NOT NULL as completed
        ''', {'user_id': user_id})
        
        # Get prerequisite relationships
        prereqs = self.db.execute_query('''
            MATCH (c1:Concept)-[:PREREQUISITE_FOR]->(c2:Concept)
            RETURN c1.id as prereq, c2.id as concept
        ''')
        
        # Build prerequisite map
        prereq_map = {}
        for p in prereqs:
            if p['concept'] not in prereq_map:
                prereq_map[p['concept']] = []
            prereq_map[p['concept']].append(p['prereq'])
        
        # AI-powered path optimization
        optimized_path = self._optimize_learning_path(concepts, prereq_map, profile)
        
        return optimized_path
    
    def generate_personalized_content(self, concept_id: str, user_id: str) -> Dict[str, Any]:
        """Generate AI-personalized learning content"""
        
        profile = self.analyze_learning_pattern(user_id)
        
        # Get concept details
        concept = self.db.execute_query('''
            MATCH (c:Concept {id: $concept_id})
            RETURN c.name as name, c.difficulty as difficulty
        ''', {'concept_id': concept_id})
        
        if not concept:
            return {}
        
        concept = concept[0]
        
        # Generate content based on learning style
        content = self._generate_adaptive_content(concept, profile)
        
        return content
    
    def calculate_mastery_score(self, user_id: str, concept_id: str) -> float:
        """Calculate AI-based mastery score for a concept"""
        
        # Get user's interaction data
        interactions = self.db.execute_query('''
            MATCH (u:User {id: $user_id})-[r:INTERACTED_WITH]->(c:Concept {id: $concept_id})
            RETURN r.time_spent as time_spent, r.attempts as attempts,
                   r.correct_answers as correct, r.total_questions as total
        ''', {'user_id': user_id, 'concept_id': concept_id})
        
        if not interactions:
            return 0.0
        
        interaction = interactions[0]
        
        # AI mastery calculation
        time_factor = min(interaction.get('time_spent', 0) / 300, 1.0)  # 5 min optimal
        accuracy = interaction.get('correct', 0) / max(interaction.get('total', 1), 1)
        attempt_penalty = max(0, 1 - (interaction.get('attempts', 1) - 1) * 0.1)
        
        mastery_score = (accuracy * 0.6 + time_factor * 0.2 + attempt_penalty * 0.2) * 100
        
        return min(mastery_score, 100)
    
    def _default_learning_profile(self) -> Dict[str, Any]:
        """Default learning profile for new users"""
        return {
            'learning_style': 'visual',
            'retention_score': 0.7,
            'optimal_pace': 'moderate',
            'difficulty_preference': 'progressive',
            'avg_attempts': 1.5,
            'total_concepts_completed': 0,
            'confidence_level': 50,
            'recommended_session_length': 30,
            'next_optimal_study_time': datetime.now() + timedelta(hours=24)
        }
    
    def _detect_learning_style(self, history: List[Dict]) -> str:
        """AI algorithm to detect learning style from interaction patterns"""
        
        # Analyze completion patterns
        quick_completions = sum(1 for h in history if h.get('attempts', 1) == 1)
        total = len(history)
        
        if quick_completions / total > 0.7:
            return 'visual'  # Quick visual learners
        elif quick_completions / total < 0.3:
            return 'kinesthetic'  # Need more practice
        else:
            return random.choice(['auditory', 'reading'])
    
    def _calculate_retention_score(self, history: List[Dict]) -> float:
        """Calculate knowledge retention using spaced repetition principles"""
        
        if not history:
            return 0.5
        
        # Simulate retention decay over time
        now = datetime.now()
        retention_sum = 0
        
        for item in history:
            timestamp = item.get('timestamp')
            if timestamp:
                try:
                    days_ago = (now - datetime.fromisoformat(timestamp)).days
                    retention = np.exp(-days_ago / 7)  # Exponential decay
                    retention_sum += retention
                except (ValueError, TypeError):
                    # If timestamp parsing fails, assume recent
                    retention_sum += 0.8
            else:
                # No timestamp, assume recent
                retention_sum += 0.8
        
        return min(retention_sum / len(history), 1.0)
    
    def _predict_learning_pace(self, history: List[Dict]) -> str:
        """Predict optimal learning pace"""
        
        if not history:
            return 'moderate'
        
        avg_attempts = sum(h.get('attempts', 1) or 1 for h in history) / len(history)
        
        if avg_attempts < 1.5:
            return 'fast'
        elif avg_attempts > 2.5:
            return 'slow'
        else:
            return 'moderate'
    
    def _analyze_difficulty_preference(self, history: List[Dict]) -> str:
        """Analyze user's difficulty preference"""
        
        if not history:
            return 'progressive'
        
        difficulties = [h.get('difficulty', 'Beginner') for h in history]
        advanced_ratio = difficulties.count('Advanced') / len(difficulties)
        
        if advanced_ratio > 0.5:
            return 'challenging'
        elif advanced_ratio < 0.2:
            return 'gentle'
        else:
            return 'progressive'
    
    def _recommend_session_length(self, history: List[Dict]) -> int:
        """Recommend optimal session length in minutes"""
        
        if not history:
            return 30
        
        # Analyze completion patterns
        avg_attempts = sum(h.get('attempts', 1) or 1 for h in history) / len(history)
        
        if avg_attempts < 1.5:
            return 45  # Can handle longer sessions
        elif avg_attempts > 2.5:
            return 20  # Shorter focused sessions
        else:
            return 30
    
    def _predict_next_study_time(self, history: List[Dict]) -> datetime:
        """Predict optimal next study time using AI"""
        
        if not history:
            return datetime.now() + timedelta(hours=24)
        
        # Simple spaced repetition algorithm
        timestamp = history[0].get('timestamp')
        if timestamp:
            try:
                last_study = datetime.fromisoformat(timestamp)
                days_since = (datetime.now() - last_study).days
            except (ValueError, TypeError):
                days_since = 0
        else:
            days_since = 0
        
        if days_since < 1:
            return datetime.now() + timedelta(hours=12)
        elif days_since < 3:
            return datetime.now() + timedelta(days=1)
        else:
            return datetime.now() + timedelta(hours=6)  # Time to review!
    
    def _optimize_learning_path(self, concepts: List[Dict], prereq_map: Dict, profile: Dict) -> List[Dict]:
        """AI-powered learning path optimization"""
        
        completed = [c for c in concepts if c['completed']]
        available = []
        
        for concept in concepts:
            if concept['completed']:
                continue
            
            # Check if prerequisites are met
            prereqs = prereq_map.get(concept['id'], [])
            if all(any(c['id'] == p and c['completed'] for c in concepts) for p in prereqs):
                available.append(concept)
        
        # AI scoring for path optimization
        scored_concepts = []
        for concept in available:
            score = self._calculate_concept_score(concept, profile)
            scored_concepts.append({
                **concept,
                'ai_score': score,
                'estimated_time': self._estimate_completion_time(concept, profile),
                'mastery_prediction': self._predict_mastery_success(concept, profile)
            })
        
        # Sort by AI score
        scored_concepts.sort(key=lambda x: x['ai_score'], reverse=True)
        
        return scored_concepts[:5]  # Top 5 recommendations
    
    def _calculate_concept_score(self, concept: Dict, profile: Dict) -> float:
        """Calculate AI score for concept recommendation"""
        
        difficulty_match = 1.0
        if profile['difficulty_preference'] == 'challenging' and concept['difficulty'] == 'Advanced':
            difficulty_match = 1.5
        elif profile['difficulty_preference'] == 'gentle' and concept['difficulty'] == 'Beginner':
            difficulty_match = 1.3
        
        confidence_factor = profile['confidence_level'] / 100
        pace_factor = 1.2 if profile['optimal_pace'] == 'fast' else 1.0
        
        return difficulty_match * confidence_factor * pace_factor * random.uniform(0.8, 1.2)
    
    def _estimate_completion_time(self, concept: Dict, profile: Dict) -> int:
        """Estimate completion time in minutes"""
        
        base_time = self.difficulty_weights.get(concept['difficulty'], 1.0) * 20
        
        if profile['optimal_pace'] == 'fast':
            return int(base_time * 0.7)
        elif profile['optimal_pace'] == 'slow':
            return int(base_time * 1.5)
        else:
            return int(base_time)
    
    def _predict_mastery_success(self, concept: Dict, profile: Dict) -> float:
        """Predict likelihood of mastering this concept"""
        
        base_success = 0.7
        
        if concept['difficulty'] == 'Beginner':
            base_success = 0.9
        elif concept['difficulty'] == 'Advanced':
            base_success = 0.5
        
        confidence_boost = (profile['confidence_level'] - 50) / 100
        
        return min(base_success + confidence_boost, 0.95)
    
    def _generate_adaptive_content(self, concept: Dict, profile: Dict) -> Dict[str, Any]:
        """Generate personalized content based on learning style"""
        
        learning_style = profile['learning_style']
        difficulty = concept['difficulty']
        
        content_templates = {
            'visual': {
                'explanation': f"🎯 {concept['name']}: Visual learners excel with diagrams and charts. This {difficulty.lower()} concept builds on your visual processing strengths.",
                'study_tips': [
                    "Create mind maps and flowcharts",
                    "Use color-coded notes",
                    "Draw concept relationships",
                    "Watch video demonstrations"
                ],
                'practice_type': 'interactive_visualization'
            },
            'auditory': {
                'explanation': f"🎵 {concept['name']}: As an auditory learner, you'll master this {difficulty.lower()} concept through discussion and verbal explanation.",
                'study_tips': [
                    "Read concepts aloud",
                    "Join study groups",
                    "Use mnemonic devices",
                    "Listen to explanatory podcasts"
                ],
                'practice_type': 'verbal_explanation'
            },
            'kinesthetic': {
                'explanation': f"🤲 {concept['name']}: Hands-on practice will help you master this {difficulty.lower()} concept through active engagement.",
                'study_tips': [
                    "Work through practice problems",
                    "Use physical manipulatives",
                    "Take frequent breaks",
                    "Apply concepts to real scenarios"
                ],
                'practice_type': 'hands_on_practice'
            },
            'reading': {
                'explanation': f"📚 {concept['name']}: Deep reading and written analysis will help you excel with this {difficulty.lower()} concept.",
                'study_tips': [
                    "Take detailed written notes",
                    "Summarize key points",
                    "Create written explanations",
                    "Use textbook resources"
                ],
                'practice_type': 'written_analysis'
            }
        }
        
        return content_templates.get(learning_style, content_templates['visual'])