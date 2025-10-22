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
        });
        if (loading) loading.style.display = 'none';
        
        // Create exactly 5 static decorative dots (if more than 1 slide)
        const dots = [];
        const dotPositions = [0, 1, 2, 3, 4]; // Tracks which dot is in which visual position
        if (testimonials.length > 1) {
            for (let i = 0; i < 5; i++) {
                const dot = createElement('span', {
                    'class': 'nav-dot',
                    'aria-hidden': 'true' // Purely decorative
                });
                navigation.appendChild(dot);
                dots.push(dot);
            }
        }
        
        // Setup carousel functionality
        let currentSlide = 0;
        let autoRotate;
        
        // Update dot positions (just visual positions, not tied to testimonials)
        function updateDotPositions() {
            dots.forEach((dot, index) => {
                const position = dotPositions[index];
                // Remove all classes
                dot.classList.remove('dot-pos-1', 'dot-pos-2', 'dot-pos-3', 'dot-pos-4', 'dot-pos-5', 'active');
                // Add position class (1-5)
                dot.classList.add(`dot-pos-${position + 1}`);
                // Middle position (2, which is pos-3) is always active
                if (position === 2) {
                    dot.classList.add('active');
                }
            });
        }
        
        // Rotate dot positions left (for right arrow / next)
        function rotateDotsLeft() {
            const last = dotPositions.pop();
            dotPositions.unshift(last);
            updateDotPositions();
        }
        
        // Rotate dot positions right (for left arrow / prev)
        function rotateDotsRight() {
            const first = dotPositions.shift();
            dotPositions.push(first);
            updateDotPositions();
        }
        
        // Initialize auto-rotation if multiple slides
        if (slides.length > 1) {
            // Show/hide arrows
            if (prevArrow) prevArrow.style.display = 'flex';
            if (nextArrow) nextArrow.style.display = 'flex';
            
            // Initialize dots
            if (dots.length > 0) {
                updateDotPositions();
            }
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
        }
        
        function showSlide(index, direction = null) {
            const previousSlide = currentSlide;
            
            // Apply exit animation to current slide
            if (direction && previousSlide !== index) {
                const oldSlide = slides[previousSlide];
                const newSlide = slides[index];
                
                // Remove any existing animation classes
                slides.forEach(slide => {
                    slide.classList.remove('slide-in-left', 'slide-in-right', 'slide-out-left', 'slide-out-right');
                });
                
                // Set up exit animation for old slide
                if (direction === 'next') {
                    oldSlide.classList.add('slide-out-left');
                    newSlide.classList.add('slide-in-right');
                } else {
                    oldSlide.classList.add('slide-out-right');
                    newSlide.classList.add('slide-in-left');
                }
                
                // Make new slide visible immediately (positioned absolutely during animation)
                newSlide.style.display = 'block';
                
                // After animation completes, update active states
                setTimeout(() => {
                    slides.forEach((slide, i) => {
                        slide.classList.toggle('active', i === index);
                        slide.setAttribute('aria-hidden', i === index ? 'false' : 'true');
                        slide.classList.remove('slide-in-left', 'slide-in-right', 'slide-out-left', 'slide-out-right');
                        // Reset display for non-active slides
                        if (i !== index) {
                            slide.style.display = '';
                        }
                    });
                }, 500);
            } else {
                // No animation, just toggle
                slides.forEach((slide, i) => {
                    slide.classList.toggle('active', i === index);
                    slide.setAttribute('aria-hidden', i === index ? 'false' : 'true');
                });
            }
            
            currentSlide = index;
            
            // Rotate dots and add dot slide animation
            if (direction && dots.length > 0) {
                // Rotate dot positions
                if (direction === 'next') {
                    rotateDotsLeft();
                } else {
                    rotateDotsRight();
                }
                
                // Add slide animation class
                navigation.classList.remove('slide-left', 'slide-right');
                // Force reflow to restart animation
                void navigation.offsetWidth;
                navigation.classList.add(direction === 'next' ? 'slide-left' : 'slide-right');
                
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
            const nextIndex = (currentSlide + 1) % slides.length;
            showSlide(nextIndex, 'next');
        }
        
        function prevSlide() {
            const prevIndex = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(prevIndex, 'prev');
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