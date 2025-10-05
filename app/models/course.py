from typing import List, Dict, Any, Optional

class Course:
    def __init__(self, db):
        self.db = db
    
    def get_all_concepts(self) -> List[Dict[str, Any]]:
        query = '''
            MATCH (c:Concept)
            RETURN c.id as id, c.name as name, c.difficulty as difficulty,
                   COALESCE(c.completed, false) as completed
            ORDER BY c.difficulty, c.name
        '''
        return self.db.execute_query(query)
    
    def get_concept_details(self, concept_id: str) -> Optional[Dict[str, Any]]:
        query = '''
            MATCH (c:Concept {id: $concept_id})
            RETURN c.id as id, c.name as name, c.difficulty as difficulty,
                   COALESCE(c.completed, false) as completed
        '''
        result = self.db.execute_query(query, {'concept_id': concept_id})
        return result[0] if result else None
    
    def get_prerequisites(self, concept_id: str) -> List[Dict[str, Any]]:
        query = '''
            MATCH (prereq:Concept)-[:PREREQUISITE_FOR]->(c:Concept {id: $concept_id})
            RETURN prereq.id as id, prereq.name as name, prereq.difficulty as difficulty
        '''
        return self.db.execute_query(query, {'concept_id': concept_id})
    
    def get_next_concepts(self, concept_id: str) -> List[Dict[str, Any]]:
        query = '''
            MATCH (c:Concept {id: $concept_id})-[:PREREQUISITE_FOR]->(next:Concept)
            RETURN next.id as id, next.name as name, next.difficulty as difficulty
        '''
        return self.db.execute_query(query, {'concept_id': concept_id})
    
    def get_learning_path(self, user_id: str = None) -> List[Dict[str, Any]]:
        if user_id:
            query = '''
                MATCH (c:Concept)
                OPTIONAL MATCH (u:User {id: $user_id})-[:COMPLETED]->(c)
                WITH c, (u IS NOT NULL) as completed
                MATCH (c)
                OPTIONAL MATCH (prereq:Concept)-[:PREREQUISITE_FOR]->(c)
                WITH c, completed, collect(prereq.id) as prerequisites
                RETURN c.id as id, c.name as name, c.difficulty as difficulty,
                       completed, prerequisites
                ORDER BY completed, c.difficulty
            '''
            return self.db.execute_query(query, {'user_id': user_id})
        else:
            return self.get_all_concepts()
