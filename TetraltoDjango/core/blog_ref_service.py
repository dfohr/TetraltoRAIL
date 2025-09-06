"""
Service layer for blog post references.
Handles business logic for fetching blog posts based on page context.
"""

from .models import BlogPost
from .blog_ref_config import BlogRefConfig
import logging

logger = logging.getLogger(__name__)

class BlogRefService:
    """Service for handling blog post references across different pages"""
    
    @staticmethod
    def get_featured_post(context):
        """
        Get the featured blog post for a specific page context.
        
        Args:
            context (str): Page context (e.g., 'services', 'home', 'torch_down')
            
        Returns:
            BlogPost or None: The featured blog post, or None if not found/configured
        """
        slug = BlogRefConfig.get_featured_post_slug(context)
        if not slug:
            logger.warning(f"No featured post configured for context: {context}")
            return None
            
        try:
            return BlogPost.objects.get(slug=slug, is_active=True)
        except BlogPost.DoesNotExist:
            logger.error(f"Featured blog post not found: {slug} for context: {context}")
            return None
    
    @staticmethod
    def get_related_posts(context, limit=None):
        """
        Get related blog posts for a specific page context.
        
        Args:
            context (str): Page context (e.g., 'services', 'torch_down')
            limit (int, optional): Maximum number of posts to return
            
        Returns:
            QuerySet: Related blog posts ordered by slug for consistency
        """
        slugs = BlogRefConfig.get_related_post_slugs(context)
        if not slugs:
            logger.warning(f"No related posts configured for context: {context}")
            return BlogPost.objects.none()
        
        queryset = BlogPost.objects.filter(
            slug__in=slugs, 
            is_active=True
        ).order_by('slug')  # Consistent ordering
        
        if limit:
            queryset = queryset[:limit]
            
        return queryset
    
    @staticmethod
    def get_blog_content_for_context(context, limit=None):
        """
        Convenience method to get both featured and related posts for a context.
        
        Args:
            context (str): Page context
            limit (int, optional): Limit for related posts
            
        Returns:
            dict: {'featured': BlogPost or None, 'related': QuerySet}
        """
        return {
            'featured': BlogRefService.get_featured_post(context),
            'related': BlogRefService.get_related_posts(context, limit)
        }