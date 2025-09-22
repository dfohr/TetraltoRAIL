/**
 * Lead Form Component - Unified JavaScript for all lead forms
 * Handles reCAPTCHA, UTM parameter capture, and form submission
 */

// UTM parameter storage
const UTM_STORAGE_KEY = 'tetralto_utm_data';
const UTM_EXPIRY_DAYS = 30;

/**
 * Store UTM parameters in localStorage with expiry
 */
function storeUTMParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const utmData = {
        timestamp: Date.now(),
        gclid: urlParams.get('gclid') || '',
        gad_campaignid: urlParams.get('gad_campaignid') || '',
        utm_source: urlParams.get('utm_source') || '',
        utm_medium: urlParams.get('utm_medium') || '',
        utm_campaign: urlParams.get('utm_campaign') || '',
        utm_term: urlParams.get('utm_term') || '',
        utm_content: urlParams.get('utm_content') || '',
    };
    
    // Only store if we have some campaign data
    const hasUTMData = Object.values(utmData).some(value => value !== '' && value !== null);
    if (hasUTMData) {
        localStorage.setItem(UTM_STORAGE_KEY, JSON.stringify(utmData));
    }
}

/**
 * Get stored UTM parameters (if not expired)
 */
function getStoredUTMParameters() {
    try {
        const stored = localStorage.getItem(UTM_STORAGE_KEY);
        if (!stored) return {};
        
        const data = JSON.parse(stored);
        const expiryTime = data.timestamp + (UTM_EXPIRY_DAYS * 24 * 60 * 60 * 1000);
        
        if (Date.now() > expiryTime) {
            localStorage.removeItem(UTM_STORAGE_KEY);
            return {};
        }
        
        return data;
    } catch (e) {
        return {};
    }
}

/**
 * Set form field value safely
 */
function setFormFieldValue(form, fieldName, value) {
    const field = form.querySelector(`input[name="${fieldName}"]`);
    if (field && value) {
        field.value = value;
    }
}

/**
 * Populate form with campaign and source data
 */
function populateFormData(form) {
    // Get current URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    
    // Get stored UTM data (fallback for sessions without query params)
    const storedUTM = getStoredUTMParameters();
    
    // Populate campaign tracking fields (prefer current URL, fallback to stored)
    setFormFieldValue(form, 'gclid', urlParams.get('gclid') || storedUTM.gclid || '');
    setFormFieldValue(form, 'gad_campaignid', urlParams.get('gad_campaignid') || storedUTM.gad_campaignid || '');
    setFormFieldValue(form, 'utm_source', urlParams.get('utm_source') || storedUTM.utm_source || '');
    setFormFieldValue(form, 'utm_medium', urlParams.get('utm_medium') || storedUTM.utm_medium || '');
    setFormFieldValue(form, 'utm_campaign', urlParams.get('utm_campaign') || storedUTM.utm_campaign || '');
    setFormFieldValue(form, 'utm_term', urlParams.get('utm_term') || storedUTM.utm_term || '');
    setFormFieldValue(form, 'utm_content', urlParams.get('utm_content') || storedUTM.utm_content || '');
    
    // Populate source and referral data
    setFormFieldValue(form, 'submission_source', window.location.pathname);
    setFormFieldValue(form, 'page_url', window.location.href);
    setFormFieldValue(form, 'referrer', document.referrer);
    
    // Populate PostHog distinct ID if available
    if (typeof posthog !== 'undefined' && posthog.get_distinct_id) {
        setFormFieldValue(form, 'posthog_distinct_id', posthog.get_distinct_id());
    }
}

/**
 * Generate reCAPTCHA token and set in form
 */
function generateRecaptchaToken(form, action) {
    return new Promise((resolve, reject) => {
        if (typeof grecaptcha === 'undefined') {
            console.warn('reCAPTCHA not loaded');
            resolve();
            return;
        }
        
        grecaptcha.ready(function() {
            // Get reCAPTCHA public key from document or use environment
            const recaptchaKey = document.body.getAttribute('data-recaptcha-key') || '';
            if (!recaptchaKey) {
                console.warn('reCAPTCHA public key not found');
                resolve();
                return;
            }
            
            grecaptcha.execute(recaptchaKey, { action: action })
                .then(function(token) {
                    setFormFieldValue(form, 'g_recaptcha_response', token);
                    setFormFieldValue(form, 'recaptcha_action', action);
                    resolve(token);
                })
                .catch(function(error) {
                    console.error('reCAPTCHA error:', error);
                    reject(error);
                });
        });
    });
}

/**
 * Initialize lead form with reCAPTCHA and tracking
 */
function initializeLeadForm(form, recaptchaAction) {
    if (!form) return;
    
    // Store UTM parameters on page load
    storeUTMParameters();
    
    // Populate form with tracking data
    populateFormData(form);
    
    // Generate initial reCAPTCHA token
    generateRecaptchaToken(form, recaptchaAction).catch(console.error);
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Refresh tracking data and reCAPTCHA token before submission
        populateFormData(form);
        
        generateRecaptchaToken(form, recaptchaAction)
            .then(function() {
                // Submit the form
                form.submit();
            })
            .catch(function(error) {
                console.error('Form submission failed:', error);
                // Submit anyway if reCAPTCHA fails (development graceful degradation)
                form.submit();
            });
    });
}

// Make function globally available
window.initializeLeadForm = initializeLeadForm;

// Auto-initialize forms with data-recaptcha-action attribute
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-recaptcha-action]');
    forms.forEach(function(form) {
        const action = form.getAttribute('data-recaptcha-action');
        if (action && !form.hasAttribute('data-initialized')) {
            form.setAttribute('data-initialized', 'true');
            initializeLeadForm(form, action);
        }
    });
});