// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function() {
            const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
            
            // Toggle menu visibility
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
            
            // Update ARIA state
            hamburger.setAttribute('aria-expanded', !isExpanded);
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navLinks.contains(event.target)) {
                navLinks.classList.remove('active');
                hamburger.classList.remove('active');
                hamburger.setAttribute('aria-expanded', 'false');
            }
        });

        // Close menu on Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                hamburger.classList.remove('active');
                hamburger.setAttribute('aria-expanded', 'false');
                hamburger.focus(); // Return focus to the toggle button
            }
        });
    }

    // Video click-to-play functionality
    const videoOverlay = document.getElementById('video-overlay');
    const youtubeVideo = document.getElementById('youtube-video');
    
    if (videoOverlay && youtubeVideo) {
        // Click to play functionality
        videoOverlay.addEventListener('click', function() {
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