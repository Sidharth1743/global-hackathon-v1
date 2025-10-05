from neo4j import GraphDatabase
import os
from typing import Dict, List, Any

class Neo4jDB:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password123')
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print(f"✅ Connected to Neo4j at {self.uri}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def execute_query(self, query: str, parameters: dict = None) -> List[Dict[str, Any]]:
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def create_sample_course(self):
        '''Initialize MIT Statistics course with sample data'''
        
        # Create constraints
        constraints = [
            "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE"
        ]
        
        for constraint in constraints:
            try:
                self.execute_query(constraint)
            except:
                pass  # Constraint might already exist
        
        # Create course
        self.execute_query('''
            MERGE (course:Course {id: 'mit-stats'})
            SET course.name = 'MIT Introduction to Probability and Statistics',
                course.description = 'Interactive graph-based statistics course'
        ''')
        
        # Create concepts with relationships
        concepts = [
            {'id': 'counting', 'name': 'Counting & Combinatorics', 'difficulty': 'Beginner'},
            {'id': 'probability', 'name': 'Basic Probability', 'difficulty': 'Beginner'},
            {'id': 'random_vars', 'name': 'Random Variables', 'difficulty': 'Intermediate'},
            {'id': 'distributions', 'name': 'Probability Distributions', 'difficulty': 'Intermediate'},
            {'id': 'bayes', 'name': 'Bayes Theorem', 'difficulty': 'Intermediate'},
            {'id': 'sampling', 'name': 'Sampling & CLT', 'difficulty': 'Advanced'},
            {'id': 'estimation', 'name': 'Statistical Estimation', 'difficulty': 'Advanced'},
            {'id': 'hypothesis', 'name': 'Hypothesis Testing', 'difficulty': 'Advanced'},
            {'id': 'regression', 'name': 'Linear Regression', 'difficulty': 'Advanced'}
        ]
        
        for concept in concepts:
            self.execute_query('''
                MERGE (c:Concept {id: $id})
                SET c.name = $name, c.difficulty = $difficulty, c.completed = false
            ''', concept)
        
        # Create prerequisite relationships
        prereqs = [
            ('counting', 'probability'),
            ('probability', 'random_vars'),
            ('random_vars', 'distributions'),
            ('probability', 'bayes'),
            ('distributions', 'sampling'),
            ('sampling', 'estimation'),
            ('estimation', 'hypothesis'),
            ('random_vars', 'regression')
        ]
        
        for prereq, concept in prereqs:
            self.execute_query('''
                MATCH (p:Concept {id: $prereq}), (c:Concept {id: $concept})
                MERGE (p)-[:PREREQUISITE_FOR]->(c)
            ''', {'prereq': prereq, 'concept': concept})
        
        # Clean up any invalid concepts
        self.execute_query('''
            MATCH (c:Concept)
            WHERE c.name IS NULL OR c.difficulty IS NULL
            DETACH DELETE c
        ''')
        
        # Link to course
        self.execute_query('''
            MATCH (course:Course {id: 'mit-stats'}), (c:Concept)
            WHERE c.name IS NOT NULL AND c.difficulty IS NOT NULL
            MERGE (course)-[:CONTAINS]->(c)
        ''')
        
        print("✅ MIT Statistics course created with 9 concepts")
    
    def get_course_graph(self) -> Dict[str, Any]:
        '''Get complete course graph for visualization'''
        
        # Get nodes (filter out invalid ones)
        nodes_query = '''
            MATCH (c:Concept)
            WHERE c.name IS NOT NULL AND c.difficulty IS NOT NULL
            RETURN c.id as id, c.name as name, c.difficulty as difficulty, 
                   COALESCE(c.completed, false) as completed
        '''
        nodes = self.execute_query(nodes_query)
        
        # Get relationships
        edges_query = '''
            MATCH (c1:Concept)-[r:PREREQUISITE_FOR]->(c2:Concept)
            RETURN c1.id as source, c2.id as target, 'prerequisite' as type
        '''
        edges = self.execute_query(edges_query)
        
        return {'nodes': nodes, 'edges': edges}
