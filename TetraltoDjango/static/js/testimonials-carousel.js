// Testimonials Carousel JavaScript - Handles multiple carousels on one page
document.addEventListener('DOMContentLoaded', function() {
    // Find all testimonial carousels on the page
    const carousels = document.querySelectorAll('.testimonials-carousel');
    
    // Initialize each carousel
    carousels.forEach(carousel => initializeCarousel(carousel));
    
    function initializeCarousel(carousel) {
        const wrapper = carousel.querySelector('.carousel-wrapper');
        const navigation = carousel.querySelector('.carousel-navigation');
        const loading = carousel.querySelector('.carousel-loading');
        const prevArrow = carousel.querySelector('.carousel-arrow-prev');
        const nextArrow = carousel.querySelector('.carousel-arrow-next');
        
        // Get testimonials from structured data (single source of truth)
        const structuredDataScript = document.querySelector('script[type="application/ld+json"]');
        let testimonials = [];
        
        if (structuredDataScript) {
            try {
                const structuredData = JSON.parse(structuredDataScript.textContent);
                
                // Parse JSON-LD ItemList format into carousel format
                if (structuredData.itemListElement && Array.isArray(structuredData.itemListElement)) {
                    testimonials = structuredData.itemListElement.map(item => {
                        const review = item.item;
                        return {
                            id: item.position, // Use position as ID
                            name: review.author?.name || 'Anonymous',
                            text: review.reviewBody || '',
                            city: review.author?.address?.addressLocality || '',
                            service: review.serviceType || 'Roofing Services',
                            rating: review.reviewRating?.ratingValue || 5,
                            url: review.url || '',
                            created_at: review.datePublished || '',
                            is_featured: true // All structured data testimonials are featured
                        };
                    });
                }
            } catch (error) {
                console.warn('Failed to parse testimonials structured data:', error);
            }
        }
        
        if (!testimonials || testimonials.length === 0) {
            // Show empty state and hide loading
            if (loading) loading.style.display = 'none';
            const emptyState = carousel.querySelector('.carousel-empty');
            if (emptyState) emptyState.style.display = 'block';
            return;
        }
        
        // Helper function to validate URL scheme for security
        function isValidUrl(url) {
            if (!url) return false;
            try {
                const urlObj = new URL(url);
                return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
            } catch {
                return false;
            }
        }
        
        // Helper function to safely create DOM elements with text content (prevents XSS)
        function createElement(tag, attributes = {}, textContent = '') {
            const element = document.createElement(tag);
            for (const [key, value] of Object.entries(attributes)) {
                element.setAttribute(key, value);
            }
            if (textContent) {
                element.textContent = textContent;
            }
            return element;
        }
        
        // Build carousel using secure DOM creation (prevents innerHTML XSS)
        const slides = [];
        const dots = [];
        
        testimonials.forEach((testimonial, index) => {
            const isActive = index === 0;
            const stars = '⭐'.repeat(Math.max(0, Math.min(5, parseInt(testimonial.rating) || 5)));
            
            // Create slide container
            const slideDiv = createElement('div', {
                'class': `testimonial-slide${isActive ? ' active' : ''}`,
                'data-slide': index,
                'aria-hidden': !isActive,
                'role': 'tabpanel',
                'aria-labelledby': `testimonial-${index}-tab`
            });
            
            // Create content container
            const contentDiv = createElement('div', { 'class': 'testimonial-content' });
            
            // Create rating stars (no rating text)
            const ratingDiv = createElement('div', {
                'class': 'rating-stars',
                'aria-label': `${testimonial.rating} out of 5 stars`
            });
            ratingDiv.textContent = stars;
            
            // Create quote with wrapper for vertical centering
            const quoteBox = createElement('div', { 'class': 'testimonial-quote-box' });
            const quote = createElement('blockquote', { 'class': 'testimonial-quote' }, testimonial.text);
            quoteBox.appendChild(quote);
            
            // Create author section
            const authorDiv = createElement('div', { 'class': 'testimonial-author' });
            const authorStrong = createElement('strong', {}, testimonial.name);
            const authorLocation = createElement('span', { 'class': 'author-location' }, testimonial.city);
            const authorService = createElement('small', { 'class': 'author-service' }, testimonial.service);
            
            authorDiv.appendChild(authorStrong);
            authorDiv.appendChild(document.createElement('br'));
            authorDiv.appendChild(authorLocation);
            authorDiv.appendChild(document.createElement('br'));
            authorDiv.appendChild(authorService);
            
            // Assemble slide (main content first)
            contentDiv.appendChild(ratingDiv);
            contentDiv.appendChild(quoteBox);
            contentDiv.appendChild(authorDiv);
            
            // Add review link at bottom with URL validation and Google logo
            if (isValidUrl(testimonial.url)) {
                const isGoogleReview = testimonial.url.includes('goo.gl') || testimonial.url.includes('google.com');
                
                const reviewLinkContainer = createElement('div', { 'class': 'review-link-container' });
                
                if (isGoogleReview) {
                    const googleLogo = createElement('img', {
                        'src': 'https://www.google.com/favicon.ico',
                        'alt': 'Google',
                        'class': 'google-logo',
                        'width': '16',
                        'height': '16'
                    });
                    reviewLinkContainer.appendChild(googleLogo);
                }
                
                const reviewLink = createElement('a', {
                    'href': testimonial.url,
                    'target': '_blank',
                    'rel': 'noopener',
                    'class': 'review-link-text',
                    'aria-label': `Read full review by ${testimonial.name} on external site`
                }, 'Read the full review here');
                
                reviewLinkContainer.appendChild(reviewLink);
                contentDiv.appendChild(reviewLinkContainer);
            }
            slideDiv.appendChild(contentDiv);
            
            wrapper.appendChild(slideDiv);
            slides.push(slideDiv);
            
            // Create navigation dot (always create, will control visibility later)
            if (testimonials.length > 1) {
                const dotButton = createElement('button', {
                    'class': `nav-dot${isActive ? ' active' : ''}`,
                    'data-slide': index,
                    'role': 'tab',
                    'id': `testimonial-${index}-tab`,
                    'aria-selected': isActive,
                    'aria-controls': `testimonial-slide-${index}`,
                    'aria-label': `View testimonial ${index + 1} by ${testimonial.name}`,
                    'style': 'display: none;' // Initially hidden, will show in updateDots
                });
                
                navigation.appendChild(dotButton);
                dots.push(dotButton);
            }
        });
        if (loading) loading.style.display = 'none';
        
        // Setup carousel functionality (use the slides/dots arrays we already created)
        const dotsElements = navigation.querySelectorAll('.nav-dot');
        let currentSlide = 0;
        let autoRotate;
        const MAX_VISIBLE_DOTS = 5;
        
        // Update which dots are visible (max 5 at a time, always centered)
        function updateDotsVisibility(direction = null) {
            if (dots.length <= MAX_VISIBLE_DOTS) {
                // Show all dots if 5 or fewer
                dots.forEach(dot => dot.style.display = 'block');
                return;
            }
            
            // Always center the window on the current slide
            let startIndex = Math.max(0, currentSlide - Math.floor(MAX_VISIBLE_DOTS / 2));
            let endIndex = Math.min(dots.length, startIndex + MAX_VISIBLE_DOTS);
            
            // Adjust if we're near the end
            if (endIndex - startIndex < MAX_VISIBLE_DOTS) {
                startIndex = Math.max(0, endIndex - MAX_VISIBLE_DOTS);
            }
            
            // Show/hide dots based on range
            dots.forEach((dot, index) => {
                if (index >= startIndex && index < endIndex) {
                    dot.style.display = 'block';
                } else {
                    dot.style.display = 'none';
                }
            });
        }
        
        // Initialize auto-rotation if multiple slides
        if (slides.length > 1) {
            // Show/hide arrows
            if (prevArrow) prevArrow.style.display = 'flex';
            if (nextArrow) nextArrow.style.display = 'flex';
            
            // Update initial dots visibility
            updateDotsVisibility();
            function startAutoRotate() {
                autoRotate = setInterval(() => {
                    nextSlide();
                }, 10000);
            }
            
            function stopAutoRotate() {
                clearInterval(autoRotate);
            }
            
            startAutoRotate();
            
            // Pause on hover or focus
            carousel.addEventListener('mouseenter', stopAutoRotate);
            carousel.addEventListener('focusin', stopAutoRotate);
            
            // Resume on mouse leave or focus out
            carousel.addEventListener('mouseleave', startAutoRotate);
            carousel.addEventListener('focusout', (e) => {
                setTimeout(() => {
                    if (!carousel.contains(document.activeElement)) {
                        startAutoRotate();
                    }
                }, 100);
            });
            
            // Dot navigation with keyboard support
            dots.forEach((dot, index) => {
                dot.addEventListener('click', () => {
                    showSlide(index);
                });
                
                dot.addEventListener('keydown', (e) => {
                    switch(e.key) {
                        case 'ArrowLeft':
                            e.preventDefault();
                            showSlide(index > 0 ? index - 1 : slides.length - 1);
                            break;
                        case 'ArrowRight':
                            e.preventDefault();
                            showSlide(index < slides.length - 1 ? index + 1 : 0);
                            break;
                        case 'Home':
                            e.preventDefault();
                            showSlide(0);
                            break;
                        case 'End':
                            e.preventDefault();
                            showSlide(slides.length - 1);
                            break;
                    }
                });
            });
        }
        
        function showSlide(index, direction = null) {
            // Update visual state
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
                slide.setAttribute('aria-hidden', i === index ? 'false' : 'true');
            });
            
            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === index);
                dot.setAttribute('aria-selected', i === index ? 'true' : 'false');
            });
            
            currentSlide = index;
            
            // Update dots visibility (always centered)
            updateDotsVisibility();
            
            // Add slide animation
            if (direction) {
                navigation.classList.remove('slide-left', 'slide-right');
                // Force reflow to restart animation
                void navigation.offsetWidth;
                navigation.classList.add(direction === 'next' ? 'slide-right' : 'slide-left');
                
                // Remove animation class after it completes
                setTimeout(() => {
                    navigation.classList.remove('slide-left', 'slide-right');
                }, 300);
            }
            
            // Announce to screen readers
            const testimonial = testimonials[index];
            carousel.setAttribute('aria-label', `Customer testimonials. Currently showing testimonial ${index + 1} of ${slides.length} by ${testimonial.name}`);
        }
        
        function nextSlide() {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide, 'next');
        }
        
        function prevSlide() {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(currentSlide, 'prev');
        }
        
        // Arrow button handlers
        if (prevArrow && slides.length > 1) {
            prevArrow.addEventListener('click', () => {
                prevSlide();
            });
        }
        
        if (nextArrow && slides.length > 1) {
            nextArrow.addEventListener('click', () => {
                nextSlide();
            });
        }
        
        // Initialize first slide announcement
        if (slides.length > 0) {
            showSlide(0);
        }
    }
});