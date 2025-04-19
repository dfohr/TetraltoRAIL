# TetraltoRail Microservices Architecture

## Overview

This document outlines the planned microservices architecture for the TetraltoRail project. The goal is to create a series of lightweight, independent services that work together to provide visitor tracking, geolocation, and notification capabilities, while maintaining a minimal impact on the main website's performance.

## Current Context

- **Website Traffic**: Low volume (~10 visitors per day)
- **Main Application**: Django-based website (in `liftoff` directory)
- **Databases**: 
  - Public PostgreSQL: Main website database, exposed to web traffic
  - Postgres-Internal: Internal services database, not exposed to web
- **Hosting**: Railway.app with direct code uploads via `railway up`
- **Static Files**: Using WhiteNoise for static file serving

## Architecture Overview

The planned architecture consists of:

1. **Main Django Website**
   - Core business functionality
   - Thin tracking layer that captures visitor data
   - Sends events to processing services

2. **Geolocation Microservice**
   - Abstracts interaction with MaxMind API
   - Translates IP addresses to location data
   - Simple API with standardized response format

3. **Visitor Analytics Service**
   - Processes raw visit data
   - Deduplicates visitors
   - Analyzes sessions and user journeys
   - Tracks visitor behavior and engagement
   - Triggers notifications for real visitors (not bots)

4. **Notification Service**
   - Sends SMS/notifications about new visitors
   - Configurable notification rules
   - Integration with SMS providers

## Detailed Service Specifications

### 1. Geolocation Microservice

**Purpose**: Provide a simple, consistent interface for IP geolocation that abstracts the underlying provider (MaxMind).

**API Endpoints**:
- `GET /geolocate?ip=<ip_address>` - Returns location data for an IP
- `GET /health` - Health check endpoint

**Tech Stack**:
- Python with FastAPI
- Requests library for MaxMind API communication

**Environment Variables**:
- `MAXMIND_API_KEY` - API key for MaxMind
- `PORT` - Port to run the service on (defaults to 8000)

**Deployment**:
- Direct upload via `railway up`
- No Docker required
- Uses Railway's Nixpacks for automatic detection

### 2. Visitor Analytics Service

**Purpose**: Track and analyze visitor behavior to provide insights and trigger notifications.

**Functionality**:
- Receive visit events from the main website
- Enrich visit data with geolocation information
- Detect and filter bot traffic
- Identify unique visitor sessions
- Track visitor engagement metrics
- Trigger notification events for genuine visitors

**API Endpoints**:
- `POST /visits` - Record a new visit
- `GET /visits` - Retrieve processed visit data
- `GET /health` - Health check endpoint

**Tech Stack**:
- Python with FastAPI
- SQLAlchemy for database operations
- Alembic for database migrations
- Requests library for service communication

**Environment Variables**:
- `DATABASE_URL` - Connection string for PostgreSQL
- `GEO_SERVICE_URL` - URL of the geolocation service
- `NOTIFICATION_SERVICE_URL` - URL of the notification service
- `PORT` - Port to run the service on (defaults to 8000)

**Data Storage**:
- Uses Postgres-Internal database
- Dedicated schema for visitor analytics
- Optimized for time-series analytics
- Tables for visits, sessions, and analytics
- Not exposed to web traffic

### 3. Notification Service

**Purpose**: Send notifications about website visitors through various channels.

**Functionality**:
- Receive notification requests from the analytics service
- Send SMS notifications via provider API
- Future capability for multiple notification channels
- Rate limiting and notification rules

**API Endpoints**:
- `POST /notify` - Send a notification
- `GET /health` - Health check endpoint

**Tech Stack**:
- Python with FastAPI
- SMS provider client library

**Environment Variables**:
- `SMS_API_KEY` - API key for SMS provider
- `NOTIFICATION_PHONE_NUMBER` - Phone number to send notifications to
- `PORT` - Port to run the service on (defaults to 8000)

## Communication Flow

1. **Visitor Arrives at Website**:
   - Django middleware captures minimal visit data
   - Creates event with timestamp, URL, IP, user agent

2. **Visit Processing**:
   - Visitor Analytics service receives visit data
   - Calls geolocation service to enrich with location data
   - Applies bot detection and session logic
   - Tracks visitor engagement metrics
   - Determines if notification should be sent

3. **Notification**:
   - If visit is from a real user, notification service is called
   - SMS is sent with visitor information

## Local Development Setup

Run multiple services locally using different terminal windows or a process manager:

```bash
# Terminal 1 - Geolocation Service
cd geo-service
export MAXMIND_API_KEY=your_dev_key
python app.py --port 8001

# Terminal 2 - Visitor Analytics Service 
cd visitor-analytics-service
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres_internal_dev
export GEO_SERVICE_URL=http://localhost:8001
python -m uvicorn app.main:app --port 8002

# Terminal 3 - Notification Service
cd notification-service
export SMS_API_KEY=your_dev_key
python app.py --port 8003

# Terminal 4 - Main Django App
cd liftoff
export VISITOR_ANALYTICS_SERVICE_URL=http://localhost:8002
python manage.py runserver
```

## Project Structure

```
TetraltoRail/
├── liftoff/                # Main Django website
├── geo-service/            # Geolocation microservice
│   ├── app.py
│   ├── requirements.txt
│   └── railway.json
├── visitor-analytics-service/  # Visitor analytics service
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   └── api/
│   ├── requirements.txt
│   └── railway.toml
└── notification-service/   # Notification service
    ├── app.py
    ├── requirements.txt
    └── railway.json
```

## Implementation Plan

### Phase 1: Basic Infrastructure
1. Create the geolocation service (simplest to test)
2. Set up the basic visit tracking in the Django app
3. Create a minimal visitor analytics service that can receive events

### Phase 2: Core Functionality
1. Implement visitor session management in the analytics service
2. Create the notification service
3. Connect all services to test the full flow

### Phase 3: Refinement
1. Add bot detection to reduce false notifications
2. Improve geolocation accuracy and error handling
3. Add more notification channels (email, push, etc.)

## Considerations for the Future

- **Scaling**: Current design is optimized for simplicity, not high volume
- **Caching**: Add caching if traffic increases
- **Additional Data**: Capture more visitor data as needed
- **Analytics**: Expand to provide comprehensive visitor analytics
- **Mobile App Integration**: Prepare for future mobile app that will receive notifications

## Service Integration with Main Website

The Django application will need minimal changes:

1. Add middleware to capture visit data
2. Create background task or asynchronous call to the analytics service
3. Ensure no impact on website performance

## Conclusion

This architecture provides a flexible, maintainable approach to visitor tracking and notifications. By separating concerns into microservices, we can iterate on each component independently while maintaining a clear, decoupled system design. 