"""
Google Drive API utilities for querying project media files.

This module provides helper functions to authenticate with Google Drive
using a service account and query files based on custom properties/labels.
"""

import json
import logging
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from django.conf import settings
import io

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_drive_service():
    """
    Initialize and return Google Drive API service with service account credentials.
    
    Returns:
        Resource: Google Drive API service object
        
    Raises:
        ValueError: If credentials are not configured
        Exception: If authentication fails
    """
    credentials_json = settings.GOOGLE_DRIVE_CREDENTIALS
    
    if not credentials_json:
        raise ValueError("GOOGLE_DRIVE_CREDENTIALS not configured in environment")
    
    try:
        # Parse JSON string if it's a string
        if isinstance(credentials_json, str):
            credentials_info = json.loads(credentials_json)
        else:
            credentials_info = credentials_json
            
        # Create credentials from service account info
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES
        )
        
        # Build and return Drive service
        service = build('drive', 'v3', credentials=credentials)
        logger.info("Google Drive service initialized successfully")
        return service
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GOOGLE_DRIVE_CREDENTIALS JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize Google Drive service: {e}")
        raise


def query_files_by_project(project_tag: str, max_results: int = 50) -> List[Dict]:
    """
    Query Google Drive files with custom property 'Project' matching project_tag.
    
    Args:
        project_tag: Value of the 'Project' custom property to filter by
        max_results: Maximum number of files to return (default: 50)
        
    Returns:
        List of dictionaries containing file metadata:
        - id: File ID
        - name: File name
        - mimeType: MIME type
        - thumbnailLink: Thumbnail URL (if available)
        - webViewLink: Web view URL
        - webContentLink: Direct download URL (if available)
        - properties: Custom properties dict
        
    Raises:
        Exception: If Drive API query fails
    """
    try:
        service = get_drive_service()
        
        # Build query for files with Project custom property
        # Note: Custom properties are searchable with 'properties has' syntax
        query = f"properties has {{ key='Project' and value='{project_tag}' }} and trashed=false"
        
        logger.info(f"Querying Drive with: {query}")
        
        # Execute search
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, thumbnailLink, webViewLink, webContentLink, properties)",
            pageSize=max_results,
            orderBy='createdTime desc'
        ).execute()
        
        files = results.get('files', [])
        logger.info(f"Found {len(files)} files for project '{project_tag}'")
        
        return files
        
    except HttpError as e:
        logger.error(f"Google Drive API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error querying Drive files: {e}")
        raise


def get_images_from_files(files: List[Dict], limit: int = 3) -> List[Dict]:
    """
    Filter and return only image files from a file list.
    
    Args:
        files: List of file dictionaries from Drive API
        limit: Maximum number of images to return
        
    Returns:
        List of image file dictionaries (limited by limit parameter)
    """
    images = [f for f in files if f.get('mimeType', '').startswith('image/')]
    return images[:limit]


def get_non_image_files(files: List[Dict], skip_count: int = 0) -> List[Dict]:
    """
    Get all non-image files or remaining files after skipping some.
    
    Args:
        files: List of file dictionaries from Drive API
        skip_count: Number of files to skip from beginning
        
    Returns:
        List of file dictionaries starting from skip_count position
    """
    return files[skip_count:] if skip_count < len(files) else []


def query_files_by_labels(project_tag: str, additional_filters: Optional[Dict[str, str]] = None, 
                          max_results: int = 50) -> List[Dict]:
    """
    Query Google Drive files with Project tag and optional additional custom property filters.
    
    This is for future use when filtering by multiple labels like PortalPage, Stage, etc.
    
    Args:
        project_tag: Value of the 'Project' custom property
        additional_filters: Dict of additional property filters (e.g., {'PortalPage': '1-Before'})
        max_results: Maximum number of files to return
        
    Returns:
        List of file dictionaries matching all filters
        
    Example:
        files = query_files_by_labels(
            '2025-10-Sherrene-Kibbe',
            {'PortalPage': '1-Before', 'Stage': 'Completed'},
            max_results=20
        )
    """
    try:
        service = get_drive_service()
        
        # Start with Project filter
        query_parts = [f"properties has {{ key='Project' and value='{project_tag}' }}"]
        
        # Add additional filters
        if additional_filters:
            for key, value in additional_filters.items():
                query_parts.append(f"properties has {{ key='{key}' and value='{value}' }}")
        
        # Add trashed=false
        query_parts.append("trashed=false")
        
        # Join with AND
        query = " and ".join(query_parts)
        
        logger.info(f"Querying Drive with multiple filters: {query}")
        
        # Execute search
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, thumbnailLink, webViewLink, webContentLink, properties)",
            pageSize=max_results,
            orderBy='createdTime desc'
        ).execute()
        
        files = results.get('files', [])
        logger.info(f"Found {len(files)} files matching filters")
        
        return files
        
    except HttpError as e:
        logger.error(f"Google Drive API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error querying Drive files with labels: {e}")
        raise


def list_all_accessible_files(max_results: int = 10) -> List[Dict]:
    """
    List all files the service account can access (for debugging).
    
    Args:
        max_results: Maximum number of files to return (default: 10)
        
    Returns:
        List of file dictionaries with all metadata including properties
    """
    try:
        service = get_drive_service()
        
        # Query all non-trashed files
        query = "trashed=false"
        
        logger.info("Listing all accessible files for debugging")
        print(f"\n{'='*80}")
        print("DRIVE API - LISTING ALL ACCESSIBLE FILES")
        print(f"Query: {query}")
        print(f"Max results: {max_results}")
        
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, thumbnailLink, webViewLink, webContentLink, properties)",
            pageSize=max_results,
            orderBy='modifiedTime desc'
        ).execute()
        
        print(f"\nComplete API Response:")
        print(json.dumps(results, indent=2, default=str))
        print(f"{'='*80}\n")
        
        files = results.get('files', [])
        logger.info(f"Service account can access {len(files)} files")
        print(f"Found {len(files)} total accessible files")
        
        if len(files) == 0:
            print("⚠️  WARNING: Service account cannot see ANY files!")
            print("This means either:")
            print("  1. No files are shared with the service account")
            print("  2. Files are shared but not with proper permissions")
            print("  3. Service account email might be incorrect")
        
        return files
        
    except HttpError as e:
        logger.error(f"Google Drive API error: {e}")
        print(f"\n❌ HTTP Error from Drive API:")
        print(f"Status: {e.resp.status}")
        print(f"Reason: {e.resp.reason}")
        print(f"Details: {e.content}")
        raise
    except Exception as e:
        logger.error(f"Error listing accessible files: {e}")
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        raise


def download_file_content(file_id: str) -> tuple:
    """
    Download file content from Google Drive.
    
    Args:
        file_id: Google Drive file ID
        
    Returns:
        tuple: (file_content: bytes, mime_type: str)
        
    Raises:
        Exception: If file download fails
    """
    try:
        service = get_drive_service()
        
        # Get file metadata for MIME type
        file_metadata = service.files().get(fileId=file_id, fields='mimeType').execute()
        mime_type = file_metadata.get('mimeType', 'application/octet-stream')
        
        # Download file content
        request = service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        # Return file content and MIME type
        file_buffer.seek(0)
        return file_buffer.read(), mime_type
        
    except HttpError as e:
        logger.error(f"Google Drive API error downloading file {file_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
        raise
