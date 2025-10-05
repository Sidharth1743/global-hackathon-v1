"""
Advanced Gamification System
Achievement system, skill trees, and competitive learning
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class GamificationEngine:
    def __init__(self, db):
        self.db = db
        self.achievements = self._load_achievements()
        self.skill_trees = self._load_skill_trees()
        
    def _load_achievements(self) -> Dict[str, Dict]:
        """Load achievement definitions"""
        return {
            'first_steps': {
                'name': '🚀 First Steps',
                'description': 'Complete your first concept',
                'points': 100,
                'type': 'milestone',
                'condition': lambda stats: stats['concepts_completed'] >= 1
            },
            'speed_demon': {
                'name': '⚡ Speed Demon',
                'description': 'Complete 3 concepts in one day',
                'points': 250,
                'type': 'performance',
                'condition': lambda stats: stats['concepts_today'] >= 3
            },
            'perfectionist': {
                'name': '💎 Perfectionist',
                'description': 'Complete 5 concepts with 100% accuracy',
                'points': 500,
                'type': 'mastery',
                'condition': lambda stats: stats['perfect_completions'] >= 5
            },
            'knowledge_seeker': {
                'name': '🔍 Knowledge Seeker',
                'description': 'Complete 10 concepts',
                'points': 300,
                'type': 'milestone',
                'condition': lambda stats: stats['concepts_completed'] >= 10
            },
            'master_learner': {
                'name': '🎓 Master Learner',
                'description': 'Complete all concepts in a difficulty level',
                'points': 1000,
                'type': 'mastery',
                'condition': lambda stats: stats['difficulty_mastered'] > 0
            },
            'streak_master': {
                'name': '🔥 Streak Master',
                'description': 'Maintain a 7-day learning streak',
                'points': 750,
                'type': 'consistency',
                'condition': lambda stats: stats['current_streak'] >= 7
            },
            'collaboration_champion': {
                'name': '🤝 Collaboration Champion',
                'description': 'Help 5 other learners',
                'points': 400,
                'type': 'social',
                'condition': lambda stats: stats['helped_others'] >= 5
            },
            'ai_whisperer': {
                'name': '🤖 AI Whisperer',
                'description': 'Use AI recommendations 10 times',
                'points': 200,
                'type': 'engagement',
                'condition': lambda stats: stats['ai_interactions'] >= 10
            }
        }
    
    def _load_skill_trees(self) -> Dict[str, Dict]:
        """Load skill tree definitions"""
        return {
            'statistics_fundamentals': {
                'name': 'Statistics Fundamentals',
                'icon': '📊',
                'levels': [
                    {'name': 'Novice', 'required_points': 0, 'bonus': 'Basic progress tracking'},
                    {'name': 'Apprentice', 'required_points': 500, 'bonus': '+10% XP for beginner concepts'},
                    {'name': 'Practitioner', 'required_points': 1500, 'bonus': 'Unlock advanced hints'},
                    {'name': 'Expert', 'required_points': 3000, 'bonus': '+20% XP for all concepts'},
                    {'name': 'Master', 'required_points': 5000, 'bonus': 'Unlock teaching mode'}
                ]
            },
            'learning_efficiency': {
                'name': 'Learning Efficiency',
                'icon': '⚡',
                'levels': [
                    {'name': 'Beginner', 'required_points': 0, 'bonus': 'Standard learning speed'},
                    {'name': 'Focused', 'required_points': 300, 'bonus': 'Reduced distraction penalties'},
                    {'name': 'Optimized', 'required_points': 800, 'bonus': 'AI-powered study recommendations'},
                    {'name': 'Accelerated', 'required_points': 2000, 'bonus': 'Fast-track learning paths'},
                    {'name': 'Transcendent', 'required_points': 4000, 'bonus': 'Instant mastery detection'}
                ]
            },
            'collaboration_master': {
                'name': 'Collaboration Master',
                'icon': '🤝',
                'levels': [
                    {'name': 'Solo', 'required_points': 0, 'bonus': 'Individual learning only'},
                    {'name': 'Helper', 'required_points': 200, 'bonus': 'Can assist other learners'},
                    {'name': 'Mentor', 'required_points': 600, 'bonus': 'Unlock group study sessions'},
                    {'name': 'Leader', 'required_points': 1200, 'bonus': 'Create learning communities'},
                    {'name': 'Guru', 'required_points': 2500, 'bonus': 'Global leaderboard access'}
                ]
            }
        }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics for gamification"""
        
        # Get basic completion stats
        basic_stats = self.db.execute_query('''
            MATCH (u:User {id: $user_id})
            OPTIONAL MATCH (u)-[c:COMPLETED]->(concept:Concept)
            OPTIONAL MATCH (u)-[h:HELPED]->(other:User)
            OPTIONAL MATCH (u)-[ai:AI_INTERACTION]->()
            RETURN 
                COUNT(DISTINCT concept) as concepts_completed,
                COUNT(DISTINCT h) as helped_others,
                COUNT(DISTINCT ai) as ai_interactions,
                u.total_points as total_points,
                u.current_streak as current_streak
        ''', {'user_id': user_id})
        
        if not basic_stats:
            return self._default_user_stats()
        
        stats = basic_stats[0]
        
        # Get today's completions
        today_stats = self.db.execute_query('''
            MATCH (u:User {id: $user_id})-[c:COMPLETED]->(concept:Concept)
            WHERE date(c.timestamp) = date()
            RETURN COUNT(*) as concepts_today
        ''', {'user_id': user_id})
        
        stats['concepts_today'] = today_stats[0]['concepts_today'] if today_stats else 0
        
        # Get perfect completions
        perfect_stats = self.db.execute_query('''
            MATCH (u:User {id: $user_id})-[c:COMPLETED]->(concept:Concept)
            WHERE c.accuracy >= 1.0
            RETURN COUNT(*) as perfect_completions
        ''', {'user_id': user_id})
        
        stats['perfect_completions'] = perfect_stats[0]['perfect_completions'] if perfect_stats else 0
        
        # Check difficulty mastery
        mastery_stats = self.db.execute_query('''
            MATCH (concept:Concept)
            WITH concept.difficulty as difficulty, COUNT(*) as total_concepts
            MATCH (u:User {id: $user_id})-[:COMPLETED]->(c:Concept {difficulty: difficulty})
            WITH difficulty, total_concepts, COUNT(*) as completed_concepts
            WHERE completed_concepts = total_concepts
            RETURN COUNT(*) as difficulty_mastered
        ''', {'user_id': user_id})
        
        stats['difficulty_mastered'] = mastery_stats[0]['difficulty_mastered'] if mastery_stats else 0
        
        # Calculate level and XP
        total_points = stats.get('total_points', 0) or 0
        level_info = self._calculate_level(total_points)
        stats.update(level_info)
        
        return dict(stats)
    
    def check_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Check and award new achievements"""
        
        stats = self.get_user_stats(user_id)
        
        # Get user's current achievements
        current_achievements = self.db.execute_query('''
            MATCH (u:User {id: $user_id})-[:EARNED]->(a:Achievement)
            RETURN a.achievement_id as id
        ''', {'user_id': user_id})
        
        earned_ids = {a['id'] for a in current_achievements}
        new_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in earned_ids:
                if achievement['condition'](stats):
                    # Award achievement
                    self._award_achievement(user_id, achievement_id, achievement)
                    new_achievements.append({
                        'id': achievement_id,
                        'name': achievement['name'],
                        'description': achievement['description'],
                        'points': achievement['points']
                    })
        
        return new_achievements
    
    def get_leaderboard(self, timeframe: str = 'all_time') -> List[Dict[str, Any]]:
        """Get leaderboard data"""
        
        if timeframe == 'weekly':
            query = '''
                MATCH (u:User)-[c:COMPLETED]->(concept:Concept)
                WHERE c.timestamp >= datetime() - duration('P7D')
                WITH u, COUNT(*) as weekly_completions, SUM(c.points) as weekly_points
                RETURN u.name as name, u.id as user_id, weekly_completions as completions, 
                       weekly_points as points, u.avatar as avatar
                ORDER BY weekly_points DESC, weekly_completions DESC
                LIMIT 10
            '''
        else:
            query = '''
                MATCH (u:User)
                OPTIONAL MATCH (u)-[c:COMPLETED]->(concept:Concept)
                WITH u, COUNT(c) as total_completions, COALESCE(u.total_points, 0) as total_points
                RETURN u.name as name, u.id as user_id, total_completions as completions,
                       total_points as points, u.avatar as avatar, u.level as level
                ORDER BY total_points DESC, total_completions DESC
                LIMIT 10
            '''
        
        return self.db.execute_query(query)
    
    def get_skill_tree_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's skill tree progress"""
        
        stats = self.get_user_stats(user_id)
        total_points = stats.get('total_points', 0)
        
        progress = {}
        for tree_id, tree in self.skill_trees.items():
            current_level = 0
            for i, level in enumerate(tree['levels']):
                if total_points >= level['required_points']:
                    current_level = i
                else:
                    break
            
            next_level = current_level + 1 if current_level < len(tree['levels']) - 1 else None
            
            progress[tree_id] = {
                'name': tree['name'],
                'icon': tree['icon'],
                'current_level': current_level,
                'current_level_name': tree['levels'][current_level]['name'],
                'current_bonus': tree['levels'][current_level]['bonus'],
                'next_level': next_level,
                'next_level_name': tree['levels'][next_level]['name'] if next_level is not None else None,
                'next_level_points': tree['levels'][next_level]['required_points'] if next_level is not None else None,
                'progress_to_next': self._calculate_progress_to_next_level(total_points, tree['levels'], current_level)
            }
        
        return progress
    
    def award_points(self, user_id: str, points: int, reason: str) -> Dict[str, Any]:
        """Award points to user and update level"""
        
        # Update user points
        self.db.execute_query('''
            MATCH (u:User {id: $user_id})
            SET u.total_points = COALESCE(u.total_points, 0) + $points
            RETURN u.total_points as new_total
        ''', {'user_id': user_id, 'points': points})
        
        # Log the point award
        self.db.execute_query('''
            MATCH (u:User {id: $user_id})
            CREATE (u)-[:EARNED_POINTS {
                points: $points,
                reason: $reason,
                timestamp: datetime()
            }]->(:PointAward)
        ''', {'user_id': user_id, 'points': points, 'reason': reason})
        
        # Check for new achievements
        new_achievements = self.check_achievements(user_id)
        
        # Update level
        stats = self.get_user_stats(user_id)
        
        return {
            'points_awarded': points,
            'total_points': stats['total_points'],
            'new_level': stats['level'],
            'new_achievements': new_achievements
        }
    
    def _default_user_stats(self) -> Dict[str, Any]:
        """Default stats for new users"""
        return {
            'concepts_completed': 0,
            'concepts_today': 0,
            'perfect_completions': 0,
            'helped_others': 0,
            'ai_interactions': 0,
            'total_points': 0,
            'current_streak': 0,
            'difficulty_mastered': 0,
            'level': 1,
            'xp': 0,
            'xp_to_next_level': 100
        }
    
    def _calculate_level(self, total_points: int) -> Dict[str, int]:
        """Calculate level and XP from total points"""
        
        # Level formula: level = floor(sqrt(points / 100)) + 1
        level = int((total_points / 100) ** 0.5) + 1
        
        # XP within current level
        points_for_current_level = ((level - 1) ** 2) * 100
        points_for_next_level = (level ** 2) * 100
        
        xp = total_points - points_for_current_level
        xp_to_next_level = points_for_next_level - total_points
        
        return {
            'level': level,
            'xp': xp,
            'xp_to_next_level': max(xp_to_next_level, 0)
        }
    
    def _award_achievement(self, user_id: str, achievement_id: str, achievement: Dict):
        """Award achievement to user"""
        
        self.db.execute_query('''
            MATCH (u:User {id: $user_id})
            CREATE (a:Achievement {
                achievement_id: $achievement_id,
                name: $name,
                description: $description,
                points: $points,
                earned_at: datetime()
            })
            CREATE (u)-[:EARNED]->(a)
        ''', {
            'user_id': user_id,
            'achievement_id': achievement_id,
            'name': achievement['name'],
            'description': achievement['description'],
            'points': achievement['points']
        })
        
        # Award points
        self.award_points(user_id, achievement['points'], f"Achievement: {achievement['name']}")
    
    def _calculate_progress_to_next_level(self, total_points: int, levels: List[Dict], current_level: int) -> float:
        """Calculate progress percentage to next level"""
        
        if current_level >= len(levels) - 1:
            return 100.0  # Max level reached
        
        current_points = levels[current_level]['required_points']
        next_points = levels[current_level + 1]['required_points']
        
        if next_points == current_points:
            return 100.0
        
        progress = (total_points - current_points) / (next_points - current_points)
        return min(max(progress * 100, 0), 100)