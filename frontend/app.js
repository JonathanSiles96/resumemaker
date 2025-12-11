// API Configuration
// Use relative URL for production (works with nginx reverse proxy)
// Use localhost for local development
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : '/api';

// Version check
console.log('🚀 App.js loaded - Version 20251202 (with payments)');

// State management
let workExperiences = [];
let educationEntries = [];
let experienceCounter = 0;
let educationCounter = 0;

// User state
let currentUser = {
    email: null,
    isPaid: false,
    freeUsed: false,
    canGenerate: true
};

// Payment config
let paymentConfig = {
    price: 25,
    stripePublicKey: null,
    paypalClientId: null,
    providers: {}
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    initializeDynamicSections();
    loadPaymentConfig();
    checkStoredUser();
    handlePaymentRedirect();
    trackPageView();
});

// ============== ANALYTICS ==============

function trackPageView() {
    try {
        fetch(`${API_BASE_URL}/analytics/track`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                path: window.location.pathname,
                referrer: document.referrer
            })
        }).catch(() => {}); // Silently fail
    } catch (e) {}
}

function trackEvent(eventType, metadata = null) {
    try {
        fetch(`${API_BASE_URL}/analytics/event`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event: eventType,
                email: currentUser.email,
                metadata: metadata
            })
        }).catch(() => {}); // Silently fail
    } catch (e) {}
}

// ============== USER & PAYMENT FUNCTIONS ==============

async function loadPaymentConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}/payment/config`);
        const result = await response.json();
        if (result.success) {
            paymentConfig = {
                price: result.price,
                stripePublicKey: result.providers.stripe?.public_key,
                paypalClientId: result.providers.paypal?.client_id,
                providers: result.providers
            };
            console.log('Payment config loaded:', paymentConfig);
        }
    } catch (error) {
        console.log('Payment config not available:', error);
    }
}

function checkStoredUser() {
    const storedEmail = localStorage.getItem('resumemaker_email');
    if (storedEmail) {
        currentUser.email = storedEmail;
        checkUserStatus(storedEmail);
    } else {
        // Show email modal for new users
        showEmailModal();
    }
}

async function checkUserStatus(email) {
    try {
        const response = await fetch(`${API_BASE_URL}/user/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        const result = await response.json();
        if (result.success) {
            currentUser = {
                email: email,
                isPaid: result.user.is_paid,
                freeUsed: result.user.free_used,
                canGenerate: result.user.can_generate
            };
            
            updateUserStatusDisplay();
            
            if (currentUser.isPaid) {
                console.log('✓ Paid user - unlimited access');
            } else if (!currentUser.freeUsed) {
                console.log('✓ New user - free generation available');
            } else {
                console.log('⚠ Free used - payment required');
            }
        }
    } catch (error) {
        console.log('Error checking user status:', error);
    }
}

function updateUserStatusDisplay() {
    // Update UI to show user status
    let statusBadge = document.getElementById('userStatusBadge');
    if (!statusBadge) {
        statusBadge = document.createElement('div');
        statusBadge.id = 'userStatusBadge';
        statusBadge.className = 'user-status-badge';
        const header = document.querySelector('header');
        if (header) header.appendChild(statusBadge);
    }
    
    if (currentUser.isPaid) {
        statusBadge.innerHTML = `<span class="badge badge-premium">💎 Premium</span> ${currentUser.email}`;
        statusBadge.className = 'user-status-badge premium';
    } else if (!currentUser.freeUsed) {
        statusBadge.innerHTML = `<span class="badge badge-free">🆓 Free Trial</span> ${currentUser.email}`;
        statusBadge.className = 'user-status-badge free';
    } else {
        statusBadge.innerHTML = `<span class="badge badge-locked">🔒 Upgrade Required</span> ${currentUser.email}`;
        statusBadge.className = 'user-status-badge locked';
    }
}

function showEmailModal() {
    document.getElementById('emailModal').style.display = 'flex';
}

function hideEmailModal() {
    document.getElementById('emailModal').style.display = 'none';
}

function showPaymentModal() {
    document.getElementById('paymentModal').style.display = 'flex';
}

function hidePaymentModal() {
    document.getElementById('paymentModal').style.display = 'none';
}

function showPaymentSuccessModal(email) {
    document.getElementById('successEmail').textContent = email;
    document.getElementById('paymentSuccessModal').style.display = 'flex';
}

function hidePaymentSuccessModal() {
    document.getElementById('paymentSuccessModal').style.display = 'none';
}

async function handleEmailSubmit() {
    const emailInput = document.getElementById('userEmail');
    const email = emailInput.value.trim().toLowerCase();
    
    if (!email || !email.includes('@')) {
        showMessage('Please enter a valid email address', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/user/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        const result = await response.json();
        if (result.success) {
            currentUser = {
                email: email,
                isPaid: result.user.is_paid,
                freeUsed: result.user.free_used,
                canGenerate: result.user.can_generate
            };
            
            localStorage.setItem('resumemaker_email', email);
            hideEmailModal();
            updateUserStatusDisplay();
            loadSavedData();
            
            if (currentUser.isPaid) {
                showMessage('Welcome back! You have unlimited access.', 'success');
            } else if (!currentUser.freeUsed) {
                showMessage('Welcome! Your first resume is FREE!', 'success');
            } else {
                showMessage('Welcome back! Upgrade for unlimited access.', 'info');
                showPaymentModal();
            }
        } else {
            showMessage(result.error || 'Error registering', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

// ============== PAYMENT HANDLERS ==============

async function handleStripePayment() {
    if (!currentUser.email) {
        showEmailModal();
        return;
    }
    
    trackEvent('payment_started', { provider: 'stripe' });
    
    try {
        showMessage('Redirecting to Stripe...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/payment/stripe/create-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: currentUser.email })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Redirect to Stripe Checkout
            if (result.checkout_url) {
                window.location.href = result.checkout_url;
            } else if (paymentConfig.stripePublicKey && result.session_id) {
                const stripe = Stripe(paymentConfig.stripePublicKey);
                await stripe.redirectToCheckout({ sessionId: result.session_id });
            }
        } else {
            showMessage(result.error || 'Payment error', 'error');
        }
    } catch (error) {
        showMessage('Error initiating payment: ' + error.message, 'error');
    }
}

async function handlePayPalPayment() {
    if (!currentUser.email) {
        showEmailModal();
        return;
    }
    
    trackEvent('payment_started', { provider: 'paypal' });
    
    try {
        showMessage('Redirecting to PayPal...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/payment/paypal/create-order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: currentUser.email })
        });
        
        const result = await response.json();
        
        if (result.success && result.approval_url) {
            window.location.href = result.approval_url;
        } else {
            showMessage(result.error || 'PayPal error', 'error');
        }
    } catch (error) {
        showMessage('Error initiating payment: ' + error.message, 'error');
    }
}

async function handleCryptoPayment() {
    if (!currentUser.email) {
        showEmailModal();
        return;
    }
    
    trackEvent('payment_started', { provider: 'coingate' });
    
    try {
        showMessage('Creating crypto payment...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/payment/coingate/create-order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: currentUser.email })
        });
        
        const result = await response.json();
        
        if (result.success && result.payment_url) {
            window.location.href = result.payment_url;
        } else {
            showMessage(result.error || 'Crypto payment error', 'error');
        }
    } catch (error) {
        showMessage('Error initiating payment: ' + error.message, 'error');
    }
}

function handlePaymentRedirect() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Handle Stripe redirect
    const sessionId = urlParams.get('session_id');
    if (sessionId) {
        verifyStripePayment(sessionId);
        return;
    }
    
    // Handle PayPal redirect
    const provider = urlParams.get('provider');
    const token = urlParams.get('token');
    if (provider === 'paypal' && token) {
        capturePayPalPayment(token);
        return;
    }
    
    // Handle CoinGate redirect
    if (provider === 'coingate') {
        // CoinGate uses webhooks, just refresh user status
        if (currentUser.email) {
            checkUserStatus(currentUser.email);
            showMessage('Checking payment status...', 'info');
        }
    }
    
    // Clear URL params
    if (urlParams.has('session_id') || urlParams.has('provider') || urlParams.has('token')) {
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

async function verifyStripePayment(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/payment/stripe/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const result = await response.json();
        
        if (result.success && result.paid) {
            currentUser.isPaid = true;
            currentUser.canGenerate = true;
            localStorage.setItem('resumemaker_email', result.email || currentUser.email);
            updateUserStatusDisplay();
            showPaymentSuccessModal(result.email || currentUser.email);
        } else {
            showMessage('Payment verification failed. Please contact support.', 'error');
        }
    } catch (error) {
        showMessage('Error verifying payment', 'error');
    }
    
    // Clear URL
    window.history.replaceState({}, document.title, window.location.pathname);
}

async function capturePayPalPayment(token) {
    try {
        // Get order ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        
        const response = await fetch(`${API_BASE_URL}/payment/paypal/capture-order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order_id: token })
        });
        
        const result = await response.json();
        
        if (result.success && result.paid) {
            currentUser.isPaid = true;
            currentUser.canGenerate = true;
            updateUserStatusDisplay();
            showPaymentSuccessModal(result.email || currentUser.email);
        } else {
            showMessage('PayPal payment capture failed', 'error');
        }
    } catch (error) {
        showMessage('Error capturing payment', 'error');
    }
    
    // Clear URL
    window.history.replaceState({}, document.title, window.location.pathname);
}

// Event Listeners
function initializeEventListeners() {
    // Form submission
    document.getElementById('resumeForm').addEventListener('submit', handleFormSubmit);
    
    // Job analysis
    document.getElementById('analyzeJobBtn').addEventListener('click', analyzeJobDescription);
    
    // Data management buttons
    document.getElementById('saveDataBtn').addEventListener('click', saveData);
    document.getElementById('loadDataBtn').addEventListener('click', loadSavedData);
    document.getElementById('clearFormBtn').addEventListener('click', clearForm);
    
    // Keywords display
    document.getElementById('showAllKeywordsBtn').addEventListener('click', showAllKeywords);
    document.getElementById('closeKeywordsBtn').addEventListener('click', closeAllKeywords);
    document.getElementById('keywordSearch').addEventListener('input', filterKeywords);
    
    // Dynamic sections
    document.getElementById('addCompanyBtn').addEventListener('click', addCompany);
    document.getElementById('addEducationBtn').addEventListener('click', addEducation);
    
    // Email modal
    document.getElementById('emailContinueBtn').addEventListener('click', handleEmailSubmit);
    document.getElementById('userEmail').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleEmailSubmit();
    });
    
    // Payment modal
    document.getElementById('closePaymentModal').addEventListener('click', hidePaymentModal);
    document.getElementById('payStripeBtn').addEventListener('click', handleStripePayment);
    document.getElementById('payPayPalBtn').addEventListener('click', handlePayPalPayment);
    document.getElementById('payCryptoBtn').addEventListener('click', handleCryptoPayment);
    
    // Success modal
    document.getElementById('closeSuccessModal').addEventListener('click', () => {
        hidePaymentSuccessModal();
        hidePaymentModal();
    });
    
    // Close modals on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// Initialize dynamic sections with default data
function initializeDynamicSections() {
    // Add default companies (4 companies by default)
    addCompany({ company: '', location: '', start_date: '', end_date: '' });
    addCompany({ company: '', location: '', start_date: '', end_date: '' });
    addCompany({ company: '', location: '', start_date: '', end_date: '' });
    addCompany({ company: '', location: '', start_date: '', end_date: '' });
    
    // Add default education (2 entries by default)
    addEducation({ school: '', location: '', degree: '', year: '', level: '' });
    addEducation({ school: '', location: '', degree: '', year: '', level: '' });
}

// Add Company
function addCompany(data = {}) {
    const id = ++experienceCounter;
    workExperiences.push(id);
    
    const container = document.getElementById('workExperienceContainer');
    const companyDiv = document.createElement('div');
    companyDiv.className = 'experience-simple';
    companyDiv.id = `company-${id}`;
    
    const companyNumber = workExperiences.length;
    const seniorityLabel = companyNumber === 1 ? ' (Most Recent - Senior)' : 
                          companyNumber === workExperiences.length ? ' (Earliest - Junior)' : '';
    
    companyDiv.innerHTML = `
        <button type="button" class="remove-btn" onclick="removeCompany(${id})" title="Remove Company">×</button>
        <h3>Company ${companyNumber}${seniorityLabel}</h3>
        <div class="form-row">
            <div class="form-group">
                <label for="company${id}">Company Name *</label>
                <input type="text" id="company${id}" name="company${id}" value="${data.company || ''}" placeholder="Enter company name">
            </div>
            <div class="form-group">
                <label for="company${id}_location">Location *</label>
                <input type="text" id="company${id}_location" name="company${id}_location" value="${data.location || ''}" placeholder="City, State/Country">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label for="company${id}_start">Start Date *</label>
                <input type="text" id="company${id}_start" name="company${id}_start" value="${data.start_date || ''}" placeholder="January 2022">
            </div>
            <div class="form-group">
                <label for="company${id}_end">End Date *</label>
                <input type="text" id="company${id}_end" name="company${id}_end" value="${data.end_date || ''}" placeholder="Present">
            </div>
        </div>
    `;
    
    container.appendChild(companyDiv);
    updateCompanyLabels();
}

// Remove Company
function removeCompany(id) {
    if (workExperiences.length <= 1) {
        alert('You must have at least one work experience entry.');
        return;
    }
    
    const index = workExperiences.indexOf(id);
    if (index > -1) {
        workExperiences.splice(index, 1);
    }
    
    const element = document.getElementById(`company-${id}`);
    if (element) {
        element.remove();
    }
    
    updateCompanyLabels();
}

// Update Company Labels (to reflect current numbering)
function updateCompanyLabels() {
    workExperiences.forEach((id, index) => {
        const companyDiv = document.getElementById(`company-${id}`);
        if (companyDiv) {
            const h3 = companyDiv.querySelector('h3');
            const companyNumber = index + 1;
            const seniorityLabel = companyNumber === 1 ? ' (Most Recent - Senior)' : 
                                  companyNumber === workExperiences.length ? ' (Earliest - Junior)' : '';
            h3.textContent = `Company ${companyNumber}${seniorityLabel}`;
        }
    });
}

// Add Education
function addEducation(data = {}) {
    const id = ++educationCounter;
    educationEntries.push(id);
    
    const container = document.getElementById('educationContainer');
    const educationDiv = document.createElement('div');
    educationDiv.className = 'education-simple';
    educationDiv.id = `education-${id}`;
    
    educationDiv.innerHTML = `
        <button type="button" class="remove-btn" onclick="removeEducation(${id})" title="Remove Education">×</button>
        <h3>Education ${educationEntries.length}</h3>
        <div class="form-row">
            <div class="form-group">
                <label for="education${id}_school">University/School *</label>
                <input type="text" id="education${id}_school" name="education${id}_school" value="${data.school || ''}" placeholder="University Name">
            </div>
            <div class="form-group">
                <label for="education${id}_location">Location *</label>
                <input type="text" id="education${id}_location" name="education${id}_location" value="${data.location || ''}" placeholder="City, Country">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label for="education${id}_degree">Degree *</label>
                <input type="text" id="education${id}_degree" name="education${id}_degree" value="${data.degree || ''}" placeholder="Bachelor/Master of Science in...">
            </div>
            <div class="form-group">
                <label for="education${id}_year">Year *</label>
                <input type="text" id="education${id}_year" name="education${id}_year" value="${data.year || ''}" placeholder="2015 - 2019">
            </div>
        </div>
        <div class="form-group">
            <label for="education${id}_level">Level (optional)</label>
            <input type="text" id="education${id}_level" name="education${id}_level" value="${data.level || ''}" placeholder="bachelors, masters, phd, etc.">
        </div>
    `;
    
    container.appendChild(educationDiv);
    updateEducationLabels();
}

// Remove Education
function removeEducation(id) {
    const index = educationEntries.indexOf(id);
    if (index > -1) {
        educationEntries.splice(index, 1);
    }
    
    const element = document.getElementById(`education-${id}`);
    if (element) {
        element.remove();
    }
    
    updateEducationLabels();
}

// Update Education Labels
function updateEducationLabels() {
    educationEntries.forEach((id, index) => {
        const educationDiv = document.getElementById(`education-${id}`);
        if (educationDiv) {
            const h3 = educationDiv.querySelector('h3');
            h3.textContent = `Education ${index + 1}`;
        }
    });
}

// Analyze Job Description
async function analyzeJobDescription() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    const btn = document.getElementById('analyzeJobBtn');
    
    if (!jobDescription) {
        showMessage('Please enter a job description first', 'error');
        return;
    }
    
    const originalText = btn.textContent;
    btn.textContent = 'Analyzing...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze-job`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description: jobDescription })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayAnalysisResults(result);
            showMessage('Job description analyzed successfully!', 'success');
            trackEvent('job_analyzed');
        } else {
            showMessage('Error analyzing job description: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server: ' + error.message, 'error');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Display Analysis Results
function displayAnalysisResults(result) {
    const resultsDiv = document.getElementById('analysisResults');
    const contentDiv = document.getElementById('analysisContent');
    
    let html = '<h4>Key Keywords Found in Job Description:</h4>';
    html += `<p><strong>${result.keywords.length}</strong> keywords identified</p>`;
    html += '<div class="keywords-list">';
    result.keywords.forEach(keyword => {
        html += `<span class="keyword-tag">${keyword}</span>`;
    });
    html += '</div>';
    
    html += `<h4 style="margin-top: 25px;">All Relevant Skills (${result.suggested_skills.length} total):</h4>`;
    html += '<p><small>These skills will be automatically added to your resume for optimal ATS matching.</small></p>';
    html += '<div class="keywords-list" style="margin-top: 15px;">';
    result.suggested_skills.forEach(skill => {
        html += `<span class="keyword-tag">${skill}</span>`;
    });
    html += '</div>';
    
    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Collect Form Data
function collectFormData() {
    // Collect work experience from dynamic entries
    const workExperienceData = [];
    workExperiences.forEach(id => {
        const companyEl = document.getElementById(`company${id}`);
        const locationEl = document.getElementById(`company${id}_location`);
        const startEl = document.getElementById(`company${id}_start`);
        const endEl = document.getElementById(`company${id}_end`);
        
        if (companyEl && locationEl && startEl && endEl) {
            const company = companyEl.value.trim();
            const location = locationEl.value.trim();
            const start_date = startEl.value.trim();
            const end_date = endEl.value.trim();
            
            // Only add if at least company name is filled
            if (company) {
                workExperienceData.push({
                    company,
                    location,
                    start_date,
                    end_date
                });
            }
        }
    });
    
    // Collect education from dynamic entries
    const educationData = [];
    educationEntries.forEach(id => {
        const schoolEl = document.getElementById(`education${id}_school`);
        const locationEl = document.getElementById(`education${id}_location`);
        const degreeEl = document.getElementById(`education${id}_degree`);
        const yearEl = document.getElementById(`education${id}_year`);
        const levelEl = document.getElementById(`education${id}_level`);
        
        if (schoolEl && locationEl && degreeEl && yearEl) {
            const school = schoolEl.value.trim();
            const location = locationEl.value.trim();
            const degree = degreeEl.value.trim();
            const year = yearEl.value.trim();
            const level = levelEl ? levelEl.value.trim() : '';
            
            // Only add if at least school name is filled
            if (school) {
                educationData.push({
                    school,
                    location,
                    degree,
                    year,
                    level
                });
            }
        }
    });
    
    const formData = {
        personal_info: {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            address: document.getElementById('address').value.trim(),
            linkedin: document.getElementById('linkedin').value.trim()
        },
        work_experience: workExperienceData,
        education: educationData,
        languages: document.getElementById('languages').value
            .split('\n')
            .map(l => l.trim())
            .filter(l => l),
        job_description: document.getElementById('jobDescription').value.trim()
    };
    
    return formData;
}

// Handle Form Submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Check if user is logged in
    if (!currentUser.email) {
        showEmailModal();
        return;
    }
    
    // Check if user can generate
    if (!currentUser.canGenerate && !currentUser.isPaid && currentUser.freeUsed) {
        showPaymentModal();
        return;
    }
    
    // Find the submit button (it might be outside the form now)
    let submitBtn = null;
    try {
        submitBtn = document.querySelector('button[type="submit"][form="resumeForm"]');
        if (!submitBtn) {
            submitBtn = e.target.querySelector('button[type="submit"]');
        }
    } catch (err) {
        console.log('Button lookup error:', err);
    }
    
    const originalText = submitBtn ? submitBtn.textContent : 'Generate ATS-Optimized Resume';
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating...';
    }
    loadingOverlay.style.display = 'flex';
    
    try {
        const userData = collectFormData();
        
        const response = await fetch(`${API_BASE_URL}/generate-resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_data: userData,
                job_description: userData.job_description,
                email: currentUser.email  // Include user email for access control
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Resume_${userData.personal_info.name.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0,10)}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showMessage('Resume generated successfully! Check your downloads.', 'success');
            
            // Track successful generation
            trackEvent('resume_generated');
            
            // Update user status after generation
            if (!currentUser.isPaid) {
                currentUser.freeUsed = true;
                currentUser.canGenerate = false;
                updateUserStatusDisplay();
            }
        } else {
            const error = await response.json();
            
            // Check if payment is required
            if (response.status === 402 || error.needs_payment) {
                currentUser.freeUsed = true;
                currentUser.canGenerate = false;
                updateUserStatusDisplay();
                showPaymentModal();
                return;
            }
            
            showMessage('Error generating resume: ' + (error.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    } finally {
        loadingOverlay.style.display = 'none';
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }
}

// Save Data
async function saveData() {
    try {
        const userData = collectFormData();
        
        const response = await fetch(`${API_BASE_URL}/save-data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('Data saved successfully!', 'success');
        } else {
            showMessage('Error saving data: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server: ' + error.message, 'error');
    }
}

// Load Saved Data
async function loadSavedData() {
    try {
        const response = await fetch(`${API_BASE_URL}/load-data`);
        const result = await response.json();
        
        if (result.success && result.data && result.data.personal_info) {
            populateForm(result.data);
            showMessage('Data loaded successfully!', 'success');
        }
    } catch (error) {
        console.log('No saved data found or error loading data');
    }
}

// Populate Form with Data
function populateForm(data) {
    // Personal info
    if (data.personal_info) {
        document.getElementById('name').value = data.personal_info.name || '';
        document.getElementById('email').value = data.personal_info.email || '';
        document.getElementById('phone').value = data.personal_info.phone || '';
        document.getElementById('address').value = data.personal_info.address || '';
        document.getElementById('linkedin').value = data.personal_info.linkedin || '';
    }
    
    // Job description
    if (data.job_description) {
        document.getElementById('jobDescription').value = data.job_description;
    }
    
    // Clear existing work experience and education
    clearDynamicSections();
    
    // Work experience - populate dynamic entries
    if (data.work_experience && data.work_experience.length > 0) {
        data.work_experience.forEach(exp => {
            addCompany({
                company: exp.company || '',
                location: exp.location || '',
                start_date: exp.start_date || '',
                end_date: exp.end_date || ''
            });
        });
    } else {
        // Add default empty entries if no data
        addCompany({ company: '', location: '', start_date: '', end_date: '' });
    }
    
    // Education - populate dynamic entries
    if (data.education && data.education.length > 0) {
        data.education.forEach(edu => {
            addEducation({
                school: edu.school || '',
                location: edu.location || '',
                degree: edu.degree || '',
                year: edu.year || '',
                level: edu.level || ''
            });
        });
    } else {
        // Add default empty entries if no data
        addEducation({ school: '', location: '', degree: '', year: '', level: '' });
    }
    
    // Languages
    if (data.languages && data.languages.length > 0) {
        document.getElementById('languages').value = data.languages.join('\n');
    }
}

// Clear dynamic sections
function clearDynamicSections() {
    // Clear work experience
    workExperiences.forEach(id => {
        const element = document.getElementById(`company-${id}`);
        if (element) {
            element.remove();
        }
    });
    workExperiences = [];
    experienceCounter = 0;
    
    // Clear education
    educationEntries.forEach(id => {
        const element = document.getElementById(`education-${id}`);
        if (element) {
            element.remove();
        }
    });
    educationEntries = [];
    educationCounter = 0;
}

// Clear Form
function clearForm() {
    if (confirm('Are you sure you want to clear all form data?')) {
        document.getElementById('resumeForm').reset();
        document.getElementById('analysisResults').style.display = 'none';
        
        // Clear and reinitialize dynamic sections
        clearDynamicSections();
        initializeDynamicSections();
        
        showMessage('Form cleared successfully', 'info');
    }
}

// Show Message
function showMessage(message, type = 'info') {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.style.display = 'block';
    
    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 5000);
}

// All Keywords Management
let allKeywordsData = [];

async function showAllKeywords() {
    const section = document.getElementById('allKeywordsSection');
    const content = document.getElementById('allKeywordsContent');
    
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
    
    // Load keywords if not already loaded
    if (allKeywordsData.length === 0) {
        content.innerHTML = '<div class="loading">Loading keywords...</div>';
        try {
            const response = await fetch(`${API_BASE_URL}/all-keywords`);
            const result = await response.json();
            
            if (result.success) {
                allKeywordsData = result.keywords;
                document.getElementById('keywordCount').textContent = result.total;
                displayKeywords(allKeywordsData);
            } else {
                content.innerHTML = '<div class="error">Failed to load keywords.</div>';
            }
        } catch (error) {
            content.innerHTML = '<div class="error">Error connecting to server.</div>';
        }
    } else {
        displayKeywords(allKeywordsData);
    }
}

function displayKeywords(keywords) {
    const content = document.getElementById('allKeywordsContent');
    
    if (keywords.length === 0) {
        content.innerHTML = '<div class="no-results">No keywords found matching your search.</div>';
        return;
    }
    
    let html = '<div class="keywords-grid">';
    keywords.forEach(keyword => {
        html += `<span class="keyword-tag">${keyword}</span>`;
    });
    html += '</div>';
    
    content.innerHTML = html;
}

function closeAllKeywords() {
    document.getElementById('allKeywordsSection').style.display = 'none';
}

function filterKeywords() {
    const searchTerm = document.getElementById('keywordSearch').value.toLowerCase();
    
    if (searchTerm === '') {
        displayKeywords(allKeywordsData);
    } else {
        const filtered = allKeywordsData.filter(keyword => 
            keyword.toLowerCase().includes(searchTerm)
        );
        displayKeywords(filtered);
    }
}
