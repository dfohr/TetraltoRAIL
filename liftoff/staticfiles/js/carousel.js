document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.testimonial-carousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('.testimonial-card');
    const prevButton = carousel.querySelector('.prev');
    const nextButton = carousel.querySelector('.next');
    let currentIndex = 0;
    let autoplayTimer;
    let isUserInteracting = false;

    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        
        currentIndex = (index + slides.length) % slides.length;
        slides[currentIndex].classList.add('active');
    }

    function nextSlide() {
        showSlide(currentIndex + 1);
    }

    function prevSlide() {
        showSlide(currentIndex - 1);
    }

    function startAutoplay() {
        stopAutoplay();
        if (!isUserInteracting) {
            autoplayTimer = setInterval(nextSlide, 5000);
        }
    }

    function stopAutoplay() {
        if (autoplayTimer) {
            clearInterval(autoplayTimer);
        }
    }

    function resetAutoplay() {
        stopAutoplay();
        startAutoplay();
    }

    // Add scroll event listeners to all testimonial text areas
    const testimonialTexts = document.querySelectorAll('.testimonial-text');
    testimonialTexts.forEach(text => {
        text.addEventListener('scroll', () => {
            isUserInteracting = true;
            stopAutoplay();
        });

        // Reset after user stops scrolling for 2 seconds
        let scrollTimeout;
        text.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                isUserInteracting = false;
                startAutoplay();
            }, 2000);
        });
    });

    // Event listeners for manual navigation
    prevButton.addEventListener('click', () => {
        prevSlide();
        resetAutoplay();
    });

    nextButton.addEventListener('click', () => {
        nextSlide();
        resetAutoplay();
    });

    // Pause on hover
    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);

    // Start the carousel
    showSlide(0);
    startAutoplay();
}); 