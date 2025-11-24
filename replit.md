# Tetralto Roofing Website - Replit Setup

## Overview
This project is a Django-based website for Tetralto Roofing, designed with a microservices architecture. It features a main Django application for the company website and a FastAPI geo-service for IP geolocation. The primary goal is to provide a robust, scalable, and visually appealing online presence for Tetralto Roofing, including a customer portal with integrated Google Drive media management.

## User Preferences
- **Be Direct & Honest**: If I'm wrong about something, say so directly. Don't sugarcoat or avoid criticism. I value honest feedback over politeness.
- **No Excessive Praise**: Avoid unnecessary compliments or "sucking up" behavior. Keep feedback factual and constructive.
- **Challenge Ideas When Needed**: If an approach seems problematic, speak up and suggest better alternatives.

## System Architecture
The project utilizes a microservices architecture with a Django 5.2 application (`TetraltoDjango/`) as the frontend and a FastAPI geo-service (`geo-service/`) for IP geolocation. PostgreSQL is used as the database.

**UI/UX Decisions:**
- **Responsive Design**: Homepage features a dynamic header system with CSS custom properties and unified padding for consistent responsiveness across devices.
- **Component-Based UI**: Reusable components are heavily utilized, such as the `_social_bar.html` (via context processor), `_blog_tile.html`, and `_feature_card.html` (via context processor).
- **Testimonials Carousel**: Features 5 decorative dots, directional slide animations, and professional box styling.
- **Customer Portal**: Designed with gallery pages, secure image/file proxying, and action tiles for Google reviews and inspection requests, adhering to Tetralto's official color palette.
- **HEIC Conversion**: Automatic server-side HEIC to JPEG conversion with caching and EXIF stripping for universal browser compatibility.

**Technical Implementations & Design Choices:**
- **Database**: PostgreSQL (Replit built-in database) with WhiteNoise for static files.
- **Deployment**: Configured for autoscale deployment using Gunicorn.
- **Context Processors**: Used for global availability of social links and features, optimizing database queries.
- **Code Refactoring**: Major forms refactoring to eliminate duplication and improve validation. Views are refactored to a service layer architecture following the Single Responsibility Principle.
- **Google Drive Integration**: 
  - Customer portal media display using service account authentication and label-based querying
  - Blog image proxy system for live Drive-backed images with `BlogTag` custom property
  - Secure proxying for images and files with authorization checks
- **Blog Image System**: 
  - Markdown syntax: `![alt](drive:tag-name)` transforms to `/blog/images/tag-name/` proxy URL
  - Hero images: `hero_image_filename` field supports both static files and `drive:tag-name` syntax
  - Template filter: `drive_url` converts drive references to proxy URLs or static paths
  - Two-level caching: tag→file_id (1h) + image bytes (24h) with ETag support
  - Security: Tag validation, MIME type checking (images only), BlogTag property serves as authorization
  - Backward compatible with static images (`/static/images/...`)
  - Automatic HEIC→JPEG conversion for universal browser support
  - SEO: Drive-backed hero images work with Open Graph, Twitter Cards, and Schema.org metadata
- **Caching**: DatabaseCache used to support multi-worker environments.
- **CSS Architecture**: Currently functional but noted as messy, requiring incremental cleanup.

## External Dependencies
- **PostgreSQL**: Primary database.
- **MaxMind**: Used by the FastAPI geo-service for IP geolocation (requires API keys).
- **Google Drive API**: Integrated for customer portal media management, using `google-api-python-client`, `google-auth`, and `google-auth-httplib2`.
- **pillow-heif**: For HEIC image conversion.
- **Pillow**: For image processing.