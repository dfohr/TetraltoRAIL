# Tetralto Roofing Website - Replit Setup

## Project Overview
This is a Django-based website for Tetralto Roofing company with a microservices architecture. The project includes:
- Main Django application (frontend) serving the roofing company website
- FastAPI geo-service for IP geolocation using MaxMind

## Project Architecture
- **Main Application**: Django 5.2 with PostgreSQL database
- **Frontend**: Located in `TetraltoDjango/` directory
- **Geo Service**: FastAPI microservice in `geo-service/` directory
- **Database**: PostgreSQL (Replit built-in database)
- **Static Files**: Handled by WhiteNoise
- **Production**: Configured for autoscale deployment

## Recent Changes (September 6, 2025)
- Successfully imported GitHub repository to Replit
- Installed Python 3.11 module and all project dependencies
- Set up PostgreSQL database and ran all migrations
- Loaded initial data (77 objects) from `data.json`
- Configured Django frontend to run on port 5000
- Set up deployment configuration for production
- Website is fully functional and serving at port 5000

## Configuration
- Django settings configured for Replit environment
- Database using environment variables (DATABASE_URL, PGHOST, etc.)
- Static files collected and served via WhiteNoise
- Cache control middleware configured for proper asset delivery
- ALLOWED_HOSTS set to accept all hosts for proxy compatibility

## Services
- **Main Website**: Running on port 5000 (Django frontend)
- **Geo Service**: Available but not currently running (requires MaxMind API keys)

## User Preferences
- Project successfully set up and ready for use
- All database migrations completed
- Static assets properly configured
- Website fully functional in Replit environment