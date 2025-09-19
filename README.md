# CS2 Analysis System - Basic Architecture Implementation

## Overview
This is a microservices-based Counter-Strike 2 (CS2) analysis system that allows players to:
- Find and understand patterns in their gameplay
- Discover similar players to play with/against  
- Get AI-powered coaching tips to improve their performance

## Architecture

The system consists of 9 microservices orchestrated with Docker Compose:

### Core Services
- **Frontend** (nginx): Static web interface accessible at http://localhost:8080
- **Nginx Proxy**: Reverse proxy routing `/api` requests to match_service and `/pypelyne` to pypelyne_service
- **Match Service** (port 5000): Core logic for pattern detection and player matching
- **DB API** (port 5001): PostgreSQL database interface
- **PostgreSQL**: Database backend for storing user and match data

### Integration Services  
- **Steam API** (port 5002): Integration with Steam platform for player data
- **OCR Service** (port 5003): Extracts statistics from CS2 screenshots
- **LLM/Gemini Service** (port 5004): AI-powered coaching tips and analysis
- **Pypelyne Service** (port 5005): Pipeline orchestration demonstration service

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone (https://github.com/ChristiaanSerf/Sagteware-Argitektuur-DA3.git)
   cd Sagteware-Argitektuur-DA3
   cp demoenv .env
   ```

2. **Build services**:
   ```bash
   docker compose build
   ```

3. **Start the system**:
   ```bash
   # Start core services first
   docker compose up db frontend steam_api ocr llm pypelyne_service
   
   # In another terminal, start dependent services
   docker compose up db_api match_service
   
   # Finally start nginx proxy
   docker compose up nginx
   ```

4. **Access the application**:
   Open http://localhost:8080 in your browser

## Features Tested & Working

### ✅ Pattern Analysis
- Analyzes win/loss ratios from user match history
- Returns detailed statistics including wins, losses, and calculated ratios

### ✅ Similar Player Discovery  
- Finds players with similar CS2 playtime and performance
- Integrates with Steam API for friend suggestions
- Gracefully handles missing Steam API keys with stub data

### ✅ AI Coaching Tips
- Provides personalized gameplay improvement suggestions
- Analyzes K/D ratio, ADR (Average Damage per Round), and other metrics
- Returns actionable advice like "practice nades" or "improve survival"

### ✅ Pypelyne Pipeline Demonstration
- Demonstrates pipeline orchestration concepts with multi-step processing
- Shows step-by-step execution tracking and result chaining
- Provides both simple hello-world and complex multi-step pipeline examples

## Service Health Endpoints

All services provide health check endpoints:
- Match Service: http://localhost:5000/health
- LLM Service: http://localhost:5004/health  
- OCR Service: http://localhost:5003/health
- Steam API: http://localhost:5002/health (via proxy)
- Pypelyne Service: http://localhost:5005/health

### Pypelyne API Endpoints

The Pypelyne service demonstrates pipeline orchestration concepts:
- **GET /pypelyne/hello**: Simple hello world pipeline example
- **GET/POST /pypelyne/pipeline**: Multi-step pipeline with input processing
- **GET /pypelyne/health**: Service health check

## Environment Configuration

Key environment variables in `.env`:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mydatabase
STEAM_API_KEY=          # Optional - uses stub data if not provided
GEMINI_API_KEY=         # Optional - uses rule-based tips if not provided
```

## Technology Stack

- **Frontend**: HTML/CSS/JavaScript with nginx
- **Backend Services**: Python Flask applications
- **Database**: PostgreSQL 16
- **Orchestration**: Docker Compose
- **Proxy**: Nginx reverse proxy
- **Container Registry**: Ready for GitHub Container Registry deployment

## Production Deployment

The system is designed for easy deployment to different environments:
- All services are containerized with proper Dockerfiles
- Environment-based configuration
- Ready for GitHub Container Registry (ghcr.io)
- Supports Dev/Pre-Prod environment separation

## Architecture Benefits

- **Microservices**: Each service can be scaled independently
- **Containerized**: Consistent deployment across environments  
- **Modular**: Easy to extend with new games or features
- **Resilient**: Services gracefully handle missing dependencies
- **Observable**: Health endpoints for monitoring
