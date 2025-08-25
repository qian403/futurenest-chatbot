#!/bin/bash

# Docker startup script for FutureNest Chatbot
# This script provides easy commands to manage the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the application in production mode"
    echo "  stop      Stop the application"
    echo "  restart   Restart the application"
    echo "  logs      Show application logs"
    echo "  build     Build the Docker image"
    echo "  clean     Clean up containers and images"
    echo "  setup     Initial setup (copy .env.example to .env)"
    echo ""
}

check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Warning: .env file not found!${NC}"
        echo "Run './docker-start.sh setup' to create from .env.example"
        echo "Then edit .env with your production settings"
        exit 1
    fi
}

case "$1" in
    start)
        echo -e "${GREEN}Starting FutureNest Chatbot...${NC}"
        check_env
        docker-compose up -d
        echo -e "${GREEN}Application started! Visit http://localhost:8000${NC}"
        ;;
    stop)
        echo -e "${YELLOW}Stopping FutureNest Chatbot...${NC}"
        docker-compose down
        echo -e "${GREEN}Application stopped${NC}"
        ;;
    restart)
        echo -e "${YELLOW}Restarting FutureNest Chatbot...${NC}"
        docker-compose down
        docker-compose up -d
        echo -e "${GREEN}Application restarted! Visit http://localhost:8000${NC}"
        ;;
    logs)
        docker-compose logs -f
        ;;
    build)
        echo -e "${GREEN}Building Docker image...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}Build completed${NC}"
        ;;
    clean)
        echo -e "${YELLOW}Cleaning up Docker containers and images...${NC}"
        docker-compose down -v
        docker system prune -f
        echo -e "${GREEN}Cleanup completed${NC}"
        ;;
    setup)
        if [ -f ".env" ]; then
            echo -e "${YELLOW}.env file already exists${NC}"
        else
            cp .env.example .env
            echo -e "${GREEN}.env file created from .env.example${NC}"
            echo -e "${YELLOW}Please edit .env with your production settings before starting${NC}"
        fi
        ;;
    *)
        print_usage
        exit 1
        ;;
esac