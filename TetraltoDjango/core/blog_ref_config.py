"""
Configuration for blog post references across different pages.
Centralizes which blog posts should be featured or related on specific pages.
"""

class BlogRefConfig:
    """Blog post reference configurations for different page contexts"""
    
    # Featured posts for different page sections
    FEATURED_POSTS = {
        'home': 'beautiful-new-roof-in-meadows-place',
        'services': 'beautiful-new-roof-in-meadows-place', 
        # Future pages can be added here:
        # 'torch_down': 'future-torch-down-blog-slug',
        # 'commercial': 'future-commercial-blog-slug',
    }
    
    # Related posts for different page contexts
    RELATED_POSTS = {
        'services': [
            'transforming-homes-with-quality-roofing-a-recent-p',
            'roofing-elevation-bridging-aesthetics-and-function', 
            'Stunning-Pewter-Gray-Roof-in-Sienna'
        ],
        # Future contexts:
        # 'torch_down': [],
        # 'commercial': [],
    }
    
    @classmethod
    def get_featured_post_slug(cls, context):
        """Get the featured post slug for a given context"""
        return cls.FEATURED_POSTS.get(context)
    
    @classmethod
    def get_related_post_slugs(cls, context):
        """Get the related post slugs for a given context"""
        return cls.RELATED_POSTS.get(context, [])