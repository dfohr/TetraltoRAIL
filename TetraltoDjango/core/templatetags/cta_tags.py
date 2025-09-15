from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def cta_call(css_class="button primary", phone="281-895-1213"):
    """
    Render a standardized Call CTA button.
    
    Usage:
        {% load cta_tags %}
        {% cta_call %}
        {% cta_call css_class="button secondary" %}
        {% cta_call phone="555-123-4567" %}
    """
    html = f'''
    <a href="tel:{phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}" 
       class="{css_class}"
       onclick="gtag('event', 'phone_call', {{ 'event_category': 'engagement', 'event_label': 'header_cta' }});">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 0.5rem;">
            <path d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.568 17.568 0 0 0 4.168 6.608 17.569 17.569 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.678.678 0 0 0-.58-.122L9.98 10.72a.678.678 0 0 1-.725-.332A10.76 10.76 0 0 1 5.745 6.878a.678.678 0 0 1-.332-.725l.29-1.804a.678.678 0 0 0-.122-.58L3.654 1.328z"/>
        </svg>
        Call {phone}
    </a>
    '''
    return mark_safe(html)


@register.simple_tag
def cta_estimate(css_class="button primary", url="/contact/"):
    """
    Render a standardized Get a Free Estimate CTA button.
    
    Usage:
        {% load cta_tags %}
        {% cta_estimate %}
        {% cta_estimate css_class="button secondary" %}
        {% cta_estimate url="/custom-estimate-page/" %}
    """
    html = f'''
    <a href="{url}" 
       class="{css_class}"
       onclick="gtag('event', 'estimate_request', {{ 'event_category': 'conversion', 'event_label': 'cta_button' }});">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 0.5rem;">
            <path d="M8.5 2.687c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"/>
        </svg>
        Get a Free Estimate
    </a>
    '''
    return mark_safe(html)


@register.simple_tag
def cta_services(css_class="button secondary", url="/services/"):
    """
    Render a standardized Our Services CTA button.
    
    Usage:
        {% load cta_tags %}
        {% cta_services %}
        {% cta_services css_class="button primary" %}
        {% cta_services url="/custom-services-page/" %}
    """
    html = f'''
    <a href="{url}" 
       class="{css_class}"
       onclick="gtag('event', 'services_view', {{ 'event_category': 'navigation', 'event_label': 'cta_button' }});">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 0.5rem;">
            <path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5 8 5.961 14.154 3.5 8.186 1.113zM15 4.239l-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.629 13.09a1 1 0 0 1-.629-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z"/>
        </svg>
        Our Services
    </a>
    '''
    return mark_safe(html)