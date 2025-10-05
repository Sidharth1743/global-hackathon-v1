#!/bin/bash

echo "🚀 Neo4j Interactive Learning Platform Setup"
echo "==========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "📋 Please review and update .env file with your settings"
else
    echo "✅ .env file already exists"
fi

# Build and start services
echo ""
echo "🏗️  Building and starting services..."
echo "   This may take a few minutes on first run..."

docker-compose down -v 2>/dev/null || true
docker-compose up --build -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."

# Wait for Neo4j
echo "   Waiting for Neo4j database..."
timeout=60
counter=0
while ! docker-compose exec -T neo4j cypher-shell -u neo4j -p learningplatform123 "RETURN 1" &>/dev/null; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -ge $timeout ]; then
        echo "   ❌ Neo4j took too long to start"
        docker-compose logs neo4j
        exit 1
    fi
    echo -n "."
done
echo ""
echo "   ✅ Neo4j is ready"

# Wait for web app
echo "   Waiting for web application..."
timeout=30
counter=0
while ! curl -sf http://localhost:5000/ &>/dev/null; do
    sleep 2
    counter=$((counter + 2))
    if [ $counter -ge $timeout ]; then
        echo "   ❌ Web application took too long to start"
        docker-compose logs web
        exit 1
    fi
    echo -n "."
done
echo ""
echo "   ✅ Web application is ready"

# Check service status
echo ""
echo "🔍 Service Status:"
docker-compose ps

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📱 Access your learning platform:"
echo "   🌐 Web App:      http://localhost:5000"
echo "   🔍 Neo4j Browser: http://localhost:7474"
echo ""
echo "🔑 Neo4j Credentials:"
echo "   Username: neo4j"
echo "   Password: learningplatform123"
echo ""
echo "🛠️  Management Commands:"
echo "   Stop services:    docker-compose down"
echo "   View logs:        docker-compose logs -f"
echo "   Restart:          docker-compose restart"
echo "   Update:           docker-compose up --build -d"
echo ""
echo "📚 Next Steps:"
echo "   1. Open http://localhost:5000 in your browser"
echo "   2. Register a new account"
echo "   3. Explore the MIT Statistics course"
echo "   4. Try the interactive knowledge graph"
echo ""
echo "🆘 Need help? Check the README.md file"
