"""
Real-time Collaborative Learning System
Multi-user interaction, study groups, and peer learning
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import uuid

class CollaborationEngine:
    def __init__(self, db):
        self.db = db
        self.active_sessions = {}  # In-memory session tracking
        
    def create_study_group(self, creator_id: str, name: str, description: str, 
                          max_members: int = 10, is_public: bool = True) -> str:
        """Create a new study group"""
        
        group_id = str(uuid.uuid4())
        
        self.db.execute_query('''
            CREATE (g:StudyGroup {
                id: $group_id,
                name: $name,
                description: $description,
                creator_id: $creator_id,
                max_members: $max_members,
                is_public: $is_public,
                created_at: datetime(),
                member_count: 1,
                active: true
            })
        ''', {
            'group_id': group_id,
            'name': name,
            'description': description,
            'creator_id': creator_id,
            'max_members': max_members,
            'is_public': is_public
        })
        
        # Add creator as first member
        self.join_study_group(group_id, creator_id, role='admin')
        
        return group_id
    
    def join_study_group(self, group_id: str, user_id: str, role: str = 'member') -> bool:
        """Join a study group"""
        
        # Check if group exists and has space
        group_info = self.db.execute_query('''
            MATCH (g:StudyGroup {id: $group_id})
            WHERE g.active = true
            RETURN g.member_count as current_members, g.max_members as max_members
        ''', {'group_id': group_id})
        
        if not group_info or group_info[0]['current_members'] >= group_info[0]['max_members']:
            return False
        
        # Check if already a member
        existing = self.db.execute_query('''
            MATCH (u:User {id: $user_id})-[m:MEMBER_OF]->(g:StudyGroup {id: $group_id})
            RETURN m
        ''', {'user_id': user_id, 'group_id': group_id})
        
        if existing:
            return False
        
        # Add membership
        self.db.execute_query('''
            MATCH (u:User {id: $user_id}), (g:StudyGroup {id: $group_id})
            CREATE (u)-[:MEMBER_OF {
                role: $role,
                joined_at: datetime(),
                contribution_score: 0
            }]->(g)
            SET g.member_count = g.member_count + 1
        ''', {'user_id': user_id, 'group_id': group_id, 'role': role})
        
        return True
    
    def start_collaborative_session(self, group_id: str, concept_id: str, 
                                  initiator_id: str) -> Dict[str, Any]:
        """Start a collaborative learning session"""
        
        session_id = str(uuid.uuid4())
        
        # Create session in database
        self.db.execute_query('''
            MATCH (g:StudyGroup {id: $group_id}), (c:Concept {id: $concept_id})
            CREATE (s:CollaborativeSession {
                id: $session_id,
                group_id: $group_id,
                concept_id: $concept_id,
                initiator_id: $initiator_id,
                started_at: datetime(),
                status: 'active',
                participant_count: 0
            })
            CREATE (g)-[:HAS_SESSION]->(s)
            CREATE (s)-[:FOCUSES_ON]->(c)
        ''', {
            'session_id': session_id,
            'group_id': group_id,
            'concept_id': concept_id,
            'initiator_id': initiator_id
        })
        
        # Initialize in-memory session
        self.active_sessions[session_id] = {
            'participants': {},
            'shared_notes': [],
            'questions': [],
            'progress': {},
            'chat_messages': []
        }
        
        return {
            'session_id': session_id,
            'status': 'created',
            'join_url': f'/collaborate/session/{session_id}'
        }
    
    def join_collaborative_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Join an active collaborative session"""
        
        # Verify session exists and is active
        session_info = self.db.execute_query('''
            MATCH (s:CollaborativeSession {id: $session_id})
            WHERE s.status = 'active'
            RETURN s.group_id as group_id, s.concept_id as concept_id
        ''', {'session_id': session_id})
        
        if not session_info:
            return {'error': 'Session not found or inactive'}
        
        # Verify user is member of the group
        membership = self.db.execute_query('''
            MATCH (u:User {id: $user_id})-[:MEMBER_OF]->(g:StudyGroup {id: $group_id})
            RETURN u.name as user_name
        ''', {'user_id': user_id, 'group_id': session_info[0]['group_id']})
        
        if not membership:
            return {'error': 'Not a member of this study group'}
        
        # Add to session
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                'participants': {},
                'shared_notes': [],
                'questions': [],
                'progress': {},
                'chat_messages': []
            }
        
        self.active_sessions[session_id]['participants'][user_id] = {
            'name': membership[0]['user_name'],
            'joined_at': datetime.now().isoformat(),
            'status': 'active',
            'cursor_position': None
        }
        
        # Update participant count
        self.db.execute_query('''
            MATCH (s:CollaborativeSession {id: $session_id})
            SET s.participant_count = s.participant_count + 1
        ''', {'session_id': session_id})
        
        return {
            'session_id': session_id,
            'concept_id': session_info[0]['concept_id'],
            'participants': self.active_sessions[session_id]['participants'],
            'shared_notes': self.active_sessions[session_id]['shared_notes']
        }
    
    def add_shared_note(self, session_id: str, user_id: str, note_content: str) -> Dict[str, Any]:
        """Add a note to the shared session"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        note = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'content': note_content,
            'timestamp': datetime.now().isoformat(),
            'type': 'note'
        }
        
        self.active_sessions[session_id]['shared_notes'].append(note)
        
        # Persist to database
        self.db.execute_query('''
            MATCH (s:CollaborativeSession {id: $session_id})
            CREATE (n:SharedNote {
                id: $note_id,
                user_id: $user_id,
                content: $content,
                timestamp: datetime(),
                session_id: $session_id
            })
            CREATE (s)-[:HAS_NOTE]->(n)
        ''', {
            'session_id': session_id,
            'note_id': note['id'],
            'user_id': user_id,
            'content': note_content
        })
        
        return note
    
    def ask_question(self, session_id: str, user_id: str, question: str) -> Dict[str, Any]:
        """Ask a question in the collaborative session"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        question_obj = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'question': question,
            'timestamp': datetime.now().isoformat(),
            'answers': [],
            'status': 'open'
        }
        
        self.active_sessions[session_id]['questions'].append(question_obj)
        
        # Persist to database
        self.db.execute_query('''
            MATCH (s:CollaborativeSession {id: $session_id})
            CREATE (q:Question {
                id: $question_id,
                user_id: $user_id,
                question: $question,
                timestamp: datetime(),
                session_id: $session_id,
                status: 'open'
            })
            CREATE (s)-[:HAS_QUESTION]->(q)
        ''', {
            'session_id': session_id,
            'question_id': question_obj['id'],
            'user_id': user_id,
            'question': question
        })
        
        return question_obj
    
    def answer_question(self, session_id: str, question_id: str, 
                       user_id: str, answer: str) -> Dict[str, Any]:
        """Answer a question in the session"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        # Find the question
        question_obj = None
        for q in self.active_sessions[session_id]['questions']:
            if q['id'] == question_id:
                question_obj = q
                break
        
        if not question_obj:
            return {'error': 'Question not found'}
        
        answer_obj = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'helpful_votes': 0
        }
        
        question_obj['answers'].append(answer_obj)
        
        # Persist to database
        self.db.execute_query('''
            MATCH (q:Question {id: $question_id})
            CREATE (a:Answer {
                id: $answer_id,
                user_id: $user_id,
                answer: $answer,
                timestamp: datetime(),
                helpful_votes: 0
            })
            CREATE (q)-[:HAS_ANSWER]->(a)
        ''', {
            'question_id': question_id,
            'answer_id': answer_obj['id'],
            'user_id': user_id,
            'answer': answer
        })
        
        return answer_obj
    
    def get_study_groups(self, user_id: str = None, public_only: bool = True) -> List[Dict[str, Any]]:
        """Get available study groups"""
        
        if user_id:
            # Get groups user is member of + public groups
            query = '''
                MATCH (g:StudyGroup)
                WHERE g.active = true AND (
                    g.is_public = true OR 
                    EXISTS((u:User {id: $user_id})-[:MEMBER_OF]->(g))
                )
                OPTIONAL MATCH (u:User {id: $user_id})-[m:MEMBER_OF]->(g)
                RETURN g.id as id, g.name as name, g.description as description,
                       g.member_count as member_count, g.max_members as max_members,
                       g.created_at as created_at, m IS NOT NULL as is_member
                ORDER BY g.created_at DESC
            '''
            params = {'user_id': user_id}
        else:
            # Get only public groups
            query = '''
                MATCH (g:StudyGroup)
                WHERE g.active = true AND g.is_public = true
                RETURN g.id as id, g.name as name, g.description as description,
                       g.member_count as member_count, g.max_members as max_members,
                       g.created_at as created_at, false as is_member
                ORDER BY g.created_at DESC
            '''
            params = {}
        
        return self.db.execute_query(query, params)
    
    def get_active_sessions(self, group_id: str) -> List[Dict[str, Any]]:
        """Get active collaborative sessions for a group"""
        
        return self.db.execute_query('''
            MATCH (g:StudyGroup {id: $group_id})-[:HAS_SESSION]->(s:CollaborativeSession)
            WHERE s.status = 'active'
            MATCH (s)-[:FOCUSES_ON]->(c:Concept)
            RETURN s.id as session_id, s.initiator_id as initiator_id,
                   s.started_at as started_at, s.participant_count as participant_count,
                   c.name as concept_name, c.id as concept_id
            ORDER BY s.started_at DESC
        ''', {'group_id': group_id})
    
    def get_collaboration_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's collaboration statistics"""
        
        stats = self.db.execute_query('''
            MATCH (u:User {id: $user_id})
            OPTIONAL MATCH (u)-[:MEMBER_OF]->(g:StudyGroup)
            OPTIONAL MATCH (u)-[:CREATED]->(q:Question)
            OPTIONAL MATCH (u)-[:CREATED]->(a:Answer)
            OPTIONAL MATCH (u)-[:HELPED]->(other:User)
            RETURN COUNT(DISTINCT g) as groups_joined,
                   COUNT(DISTINCT q) as questions_asked,
                   COUNT(DISTINCT a) as answers_given,
                   COUNT(DISTINCT other) as users_helped
        ''', {'user_id': user_id})
        
        if not stats:
            return {
                'groups_joined': 0,
                'questions_asked': 0,
                'answers_given': 0,
                'users_helped': 0,
                'collaboration_score': 0
            }
        
        stat = stats[0]
        
        # Calculate collaboration score
        collaboration_score = (
            stat['groups_joined'] * 10 +
            stat['questions_asked'] * 5 +
            stat['answers_given'] * 15 +
            stat['users_helped'] * 25
        )
        
        return {
            **dict(stat),
            'collaboration_score': collaboration_score
        }
    
    def send_chat_message(self, session_id: str, user_id: str, message: str) -> Dict[str, Any]:
        """Send a chat message in collaborative session"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        chat_message = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'type': 'chat'
        }
        
        self.active_sessions[session_id]['chat_messages'].append(chat_message)
        
        # Keep only last 50 messages in memory
        if len(self.active_sessions[session_id]['chat_messages']) > 50:
            self.active_sessions[session_id]['chat_messages'] = \
                self.active_sessions[session_id]['chat_messages'][-50:]
        
        return chat_message
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get complete session data for real-time updates"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        return self.active_sessions[session_id]
    
    def end_session(self, session_id: str, user_id: str) -> bool:
        """End a collaborative session"""
        
        # Check if user has permission to end session
        session_info = self.db.execute_query('''
            MATCH (s:CollaborativeSession {id: $session_id})
            MATCH (g:StudyGroup {id: s.group_id})
            MATCH (u:User {id: $user_id})-[m:MEMBER_OF]->(g)
            WHERE s.initiator_id = $user_id OR m.role = 'admin'
            RETURN s
        ''', {'session_id': session_id, 'user_id': user_id})
        
        if not session_info:
            return False
        
        # Update session status
        self.db.execute_query('''
            MATCH (s:CollaborativeSession {id: $session_id})
            SET s.status = 'ended', s.ended_at = datetime()
        ''', {'session_id': session_id})
        
        # Clean up in-memory data
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        return True