// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navLinks.contains(event.target)) {
                navLinks.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    }

    // Video lazy loading and click-to-play functionality
    const videoOverlay = document.getElementById('video-overlay');
    const youtubeVideo = document.getElementById('youtube-video');
    
    if (videoOverlay && youtubeVideo) {
        // Lazy load video when it comes into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && youtubeVideo.src === 'about:blank') {
                    youtubeVideo.src = youtubeVideo.dataset.src;
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.1
        });
        
        observer.observe(youtubeVideo);
        
        // Click to play functionality
        videoOverlay.addEventListener('click', function() {
            // Load the video if not already loaded
            if (youtubeVideo.src === 'about:blank') {
                youtubeVideo.src = youtubeVideo.dataset.src;
            }
            
            // Hide overlay and start playing
            videoOverlay.classList.add('hidden');
            
            // Add autoplay parameter to the video URL
            const currentSrc = youtubeVideo.src;
            if (!currentSrc.includes('autoplay=1')) {
                const separator = currentSrc.includes('?') ? '&' : '?';
                youtubeVideo.src = currentSrc + separator + 'autoplay=1';
            }
        });
    }
}); 