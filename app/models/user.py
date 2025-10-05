import bcrypt
import uuid
from typing import Optional, Dict, Any

class User:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        # Check if user exists
        existing = self.get_user_by_email(email)
        if existing:
            raise ValueError("User already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = str(uuid.uuid4())
        
        # Create user
        query = '''
            CREATE (u:User {id: $user_id, email: $email, name: $name, password_hash: $password_hash})
            RETURN u.id as id, u.email as email, u.name as name
        '''
        result = self.db.execute_query(query, {
            'user_id': user_id, 'email': email, 'name': name, 'password_hash': password_hash
        })
        
        return result[0] if result else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = '''
            MATCH (u:User {email: $email})
            RETURN u.id as id, u.email as email, u.name as name, u.password_hash as password_hash
        '''
        result = self.db.execute_query(query, {'email': email})
        return result[0] if result else None
    
    def verify_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return {'id': user['id'], 'email': user['email'], 'name': user['name']}
        return None
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        query = '''
            MATCH (u:User {id: $user_id})
            OPTIONAL MATCH (u)-[p:COMPLETED]->(c:Concept)
            WITH u, count(c) as completed
            MATCH (total:Concept)
            RETURN completed, count(total) as total
        '''
        result = self.db.execute_query(query, {'user_id': user_id})
        
        if result:
            completed = result[0]['completed']
            total = result[0]['total']
            percentage = (completed / total * 100) if total > 0 else 0
            return {'completed': completed, 'total': total, 'percentage': percentage}
        
        return {'completed': 0, 'total': 0, 'percentage': 0}
    
    def mark_concept_complete(self, user_id: str, concept_id: str):
        query = '''
            MATCH (u:User {id: $user_id}), (c:Concept {id: $concept_id})
            MERGE (u)-[:COMPLETED]->(c)
            SET c.completed = true
        '''
        self.db.execute_query(query, {'user_id': user_id, 'concept_id': concept_id})
