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

## Recent Changes (September 6-8, 2025)
- **Fresh Import Setup Complete**: Successfully imported GitHub repository to Replit
- **Python Environment**: Installed Python 3.11 module and all project dependencies
- **Database Setup**: Set up PostgreSQL database and ran all migrations successfully
- **Data Loading**: Loaded initial data (86 objects) from `data.json` fixture
- **Django Frontend**: Configured and running on port 5000 with all static files served correctly
- **Geo-Service**: FastAPI dependencies installed and ready (requires MaxMind API keys)
- **Production Ready**: Deployment configuration set up for autoscale with Gunicorn
- **Website Status**: Fully functional and serving at port 5000
- **Social Bar Architecture Overhaul** (September 7, 2025): Evolved through multiple iterations to optimal design
  - **Phase 1**: Converted from base template to selective reusable `_social_bar.html` component
  - **Phase 2**: Implemented template tags with self-contained data logic
  - **Phase 3**: **Final Solution** - Context processor for global availability and performance
  - **Current Implementation**: Social links loaded once per request via context processor
  - **Usage**: Pages include with `{% include '_social_bar.html' %}` - no loading or data dependencies
  - **Performance**: Single database query per request, no repeated template tag loading
  - **Maintainability**: All social links logic centralized in `core/context_processors.py`
- **Blog Tile Component System** (September 8, 2025): Built clean, reusable blog tiles
  - **Container Query Design**: Components respond to container width, not viewport
  - **Simplified Architecture**: Eliminated messy variant system for one clean design
  - **Optimal Sizing**: 340px × 288px images with auto-height tiles for uniform grids
  - **Perfect Typography**: 3-line title clamping with no text shadows and tight spacing
  - **Component Test Framework**: Created comprehensive testing page with realistic container widths (1400px/768px/375px)
  - **Production Integration**: Ready for use across website with template tag `{% blog_tile "slug" %}`
  - **CSS Cleanup**: Reduced from complex variant system to clean, maintainable single design

## Code Architecture Improvements (September 6, 2025)
- **Major Forms Refactoring**: Eliminated 100% code duplication in forms.py
  - Reduced code from 247 to 156 lines (37% reduction)
  - Unified LeadForm and GoogleLandingForm into single class with parameter control
  - Improved validation: 10-digit US phone numbers and meaningful descriptions
  - Enhanced error handling and logging
- **Views Refactoring - Fat Controllers Fix**: Implemented clean service layer architecture
  - Created BlogRefConfig and BlogRefService for centralized blog post references
  - Removed hardcoded blog slugs from views (4 hardcoded references eliminated)
  - Extracted business logic from views following Single Responsibility Principle
  - Cleaned debug print statements from production code
  - Improved maintainability and extensibility for future pages

## CSS Architecture Notes
- CSS is currently functional but architecturally messy (1,460-line components.css)
- Originally written by Claude AI with scattered media queries and inconsistent patterns
- Consider incremental cleanup approach rather than wholesale refactoring to avoid breaking the site
- Site displays perfectly but underlying CSS could be better organized

## Configuration
- Django settings configured for Replit environment
- Database using environment variables (DATABASE_URL, PGHOST, etc.)
- Static files collected and served via WhiteNoise
- Cache control middleware configured for proper asset delivery
- ALLOWED_HOSTS set to accept all hosts for proxy compatibility

## Services
- **Main Website**: Running on port 5000 (Django frontend)
- **Geo Service**: Dependencies installed, available but requires MaxMind API keys to run
- **Database**: PostgreSQL with all migrations applied and data loaded

## User Preferences & Communication Guidelines
- **Be Direct & Honest**: If I'm wrong about something, say so directly. Don't sugarcoat or avoid criticism. I value honest feedback over politeness.
- **No Excessive Praise**: Avoid unnecessary compliments or "sucking up" behavior. Keep feedback factual and constructive.
- **Challenge Ideas When Needed**: If an approach seems problematic, speak up and suggest better alternatives.

## Project Status
- Project successfully set up and ready for use
- All database migrations completed
- Static assets properly configured  
- Website fully functional in Replit environment