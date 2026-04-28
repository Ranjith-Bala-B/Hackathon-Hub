let currentUser = null;
let currentUserType = null;
let allHackathons = [];
let allRegisteredHackathons = [];
let currentHackathonId = null;
let teamMemberCount = 0;
const API_BASE_URL = window.location.origin;

document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
});

function checkLoginStatus() {
    const savedUser = localStorage.getItem('currentUser');
    const savedUserType = localStorage.getItem('userType');
    
    if (savedUser && savedUserType) {
        currentUser = JSON.parse(savedUser);
        currentUserType = savedUserType;
        loadPage('dashboard');
        updateNavbar();
    } else {
        loadPage('login');
    }
}

function updateNavbar() {
    const navbar = document.querySelector('.navbar');
    if (currentUser) {
        navbar.style.display = 'block';
    } else {
        navbar.style.display = 'none';
    }
}

function loadPage(pageName) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    const page = document.getElementById(pageName + '-page');
    if (page) {
        page.classList.add('active');
    }
    
    switch(pageName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'explore':
            loadExploreHackathons();
            break;
        case 'create-hackathon':
            initializeCreateHackathonForm();
            break;
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    if (!email || !password) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const userType = data.user_type;
            const userObj = { email: email, name: email.split('@')[0] };
            
            currentUser = userObj;
            currentUserType = userType;
            
            localStorage.setItem('currentUser', JSON.stringify(userObj));
            localStorage.setItem('userType', userType);
            
            updateNavbar();
            showMessage('Login successful!', 'success');
            
            setTimeout(() => {
                loadPage('dashboard');
            }, 1000);
        } else {
            showMessage(data.error || 'Invalid email or password', 'error');
        }
    } catch (error) {
        showMessage('Error during login', 'error');
    }
}

async function handleSignup(event) {
    event.preventDefault();
    
    let userData = {};
    const activeBtn = document.querySelector('.type-btn.active');
    const selectedType = activeBtn && activeBtn.textContent.includes('ORGANIZATION') ? 'organization' : 'student';
    
    userData.user_type = selectedType;
    
    if (selectedType === 'student') {
        userData.name = document.getElementById('student-name').value;
        userData.dob = document.getElementById('student-dob').value;
        userData.mobile = document.getElementById('student-mobile').value;
        userData.whatsapp = document.getElementById('student-whatsapp').value;
        userData.email = document.getElementById('student-email').value;
        userData.password = document.getElementById('student-password').value;
        userData.confirm_password = document.getElementById('student-confirm-password').value;
        
        if (userData.password !== userData.confirm_password) {
            showMessage('Passwords do not match', 'error');
            return;
        }
    } else {
        userData.organization_name = document.getElementById('org-name').value;
        userData.phone = document.getElementById('org-phone').value;
        userData.email = document.getElementById('org-email').value;
        userData.address = document.getElementById('org-address').value;
        userData.password = document.getElementById('org-password').value;
        userData.confirm_password = document.getElementById('org-confirm-password').value;
        
        if (userData.password !== userData.confirm_password) {
            showMessage('Passwords do not match', 'error');
            return;
        }
    }
    
    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Signup successful! Please login.', 'success');
            setTimeout(() => {
                document.getElementById('signup-form').reset();
                loadPage('login');
            }, 1500);
        } else {
            showMessage(data.error || 'Signup failed', 'error');
        }
    } catch (error) {
        showMessage('Error during signup', 'error');
    }
}

function selectUserType(type, event) {
    document.querySelectorAll('.type-btn').forEach(btn => btn.classList.remove('active'));
    event.target.closest('.type-btn').classList.add('active');
    
    document.querySelectorAll('.signup-section').forEach(section => section.classList.remove('active'));
    
    if (type === 'student') {
        document.getElementById('student-signup').classList.add('active');
    } else {
        document.getElementById('organization-signup').classList.add('active');
    }
}

async function loadDashboard() {
    const studentDashboard = document.getElementById('student-dashboard');
    const orgDashboard = document.getElementById('organization-dashboard');
    
    try {
        const response = await fetch('/dashboard');
        if (!response.ok) {
            if (response.status === 401) { logout(); return; }
            throw new Error('Failed to load dashboard');
        }
        const data = await response.json();
        
        if (data.user_type === 'student') {
            studentDashboard.style.display = 'block';
            orgDashboard.style.display = 'none';
            document.getElementById('user-name').textContent = data.data.student_name;
            loadStudentDashboard(data.data.registered_hackathons);
        } else {
            studentDashboard.style.display = 'none';
            orgDashboard.style.display = 'block';
            document.getElementById('user-name').textContent = data.data.organization_name;
            loadOrgDashboard(data.data.scheduled_hackathons);
        }
    } catch (error) {
        console.error(error);
        showMessage('Error loading dashboard', 'error');
    }
}

function loadStudentDashboard(registeredHackathons) {
    allRegisteredHackathons = registeredHackathons || [];
    const totalCount = document.getElementById('student-total-registrations');
    if (totalCount) {
        totalCount.textContent = allRegisteredHackathons.length;
    }
    
    displayRegisteredHackathons(allRegisteredHackathons);
}

function displayRegisteredHackathons(hackathons) {
    const list = document.getElementById('student-registered-list');
    
    if (!hackathons || hackathons.length === 0) {
        list.innerHTML = '<p class="empty-state">No hackathons match the selected filter. <a href="#" onclick="loadPage(\'explore\')" style="color: var(--primary-color);">Explore hackathons</a></p>';
    } else {
        list.innerHTML = hackathons.map(h => `
            <div class="scheduled-item">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <h4>${h.name}</h4>
                    <span style="font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: ${h.registration_closed ? '#fee2e2' : '#dcfce7'}; color: ${h.registration_closed ? '#dc2626' : '#166534'};">
                        ${h.registration_closed ? 'Closed' : 'Open'}
                    </span>
                </div>
                <p>📅 ${formatDate(h.datetime)}</p>
                <p>📍 ${h.location}</p>
            </div>
        `).join('');
    }
}

function filterRegisteredHackathons(type) {
    document.querySelectorAll('#student-dashboard .filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    let filtered = allRegisteredHackathons;
    if (type === 'upcoming') {
        filtered = allRegisteredHackathons.filter(h => new Date(h.datetime) > new Date());
    } else if (type === 'completed') {
        filtered = allRegisteredHackathons.filter(h => new Date(h.datetime) <= new Date());
    }
    
    displayRegisteredHackathons(filtered);
}

function loadOrgDashboard(scheduledHackathons) {
    const list = document.getElementById('org-scheduled-list');
    
    if (!scheduledHackathons || scheduledHackathons.length === 0) {
        list.innerHTML = '<p class="empty-state">No hackathons scheduled yet. <a href="#" onclick="loadPage(\'create-hackathon\')" style="color: var(--primary-color);">Create your first hackathon</a></p>';
    } else {
        list.innerHTML = scheduledHackathons.map(h => `
            <div class="scheduled-item">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <h4>${h.name}</h4>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.8rem;" onclick="viewHackathonTeams(${h.id})">View Teams</button>
                        <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.8rem; background: ${h.registration_closed ? '#dcfce7' : '#fef3c7'}; color: ${h.registration_closed ? '#166534' : '#92400e'}; border-color: ${h.registration_closed ? '#bbf7d0' : '#fde68a'};" onclick="toggleRegistration(${h.id})">
                            ${h.registration_closed ? 'Open Registration' : 'Close Registration'}
                        </button>
                        <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.8rem; background: #fee2e2; color: #dc2626; border-color: #fca5a5;" onclick="deleteHackathon(${h.id})">Delete</button>
                    </div>
                </div>
                <p>📅 ${formatDate(h.datetime)}</p>
                <p>📍 ${h.location}</p>
                <p>Registered Teams: ${h.teams || 0}</p>
                <p>Status: <span style="font-weight: bold; color: ${h.registration_closed ? '#dc2626' : '#166534'};">${h.registration_closed ? 'Registration Closed' : 'Registration Open'}</span></p>
            </div>
        `).join('');
    }
}

async function deleteHackathon(id) {
    if (!confirm("Are you sure you want to delete this hackathon? This action cannot be undone.")) {
        return;
    }
    try {
        const response = await fetch(`/api/hackathons/${id}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (response.ok) {
            showMessage('Hackathon deleted successfully', 'success');
            loadDashboard();
        } else {
            showMessage(data.error || 'Failed to delete hackathon', 'error');
        }
    } catch (error) {
        showMessage('Error deleting hackathon', 'error');
    }
}

async function toggleRegistration(id) {
    try {
        const response = await fetch(`/api/hackathons/${id}/toggle_registration`, {
            method: 'PUT'
        });
        const data = await response.json();
        if (response.ok) {
            showMessage(data.registration_closed ? 'Registration closed' : 'Registration opened', 'success');
            loadDashboard();
        } else {
            showMessage(data.error || 'Failed to toggle registration status', 'error');
        }
    } catch (error) {
        showMessage('Error toggling registration status', 'error');
    }
}

async function viewHackathonTeams(id) {
    const container = document.getElementById('teams-list-container');
    container.innerHTML = '<div class="spinner"></div> Loading teams...';
    openModal('teams-modal');
    
    try {
        const response = await fetch(`/api/hackathons/${id}/teams`);
        const data = await response.json();
        
        if (response.ok) {
            if (!data || data.length === 0) {
                container.innerHTML = '<p class="empty-state">No teams have registered for this hackathon yet.</p>';
            } else {
                container.innerHTML = data.map(team => `
                    <div class="team-card" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; color: var(--light-text); backdrop-filter: blur(10px);">
                        <h3 style="margin-top: 0; color: var(--primary-color);">${team.team_name}</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                            <div>
                                <strong>Team Leader:</strong> ${team.leader.name}<br>
                                📧 ${team.leader.email}<br>
                                📱 ${team.leader.mobile}
                            </div>
                            <div>
                                <strong>Preferences:</strong><br>
                                Food & Stay: ${team.food_stay || 'Not specified'}<br>
                                ${team.problem_statement ? `Problem: ${team.problem_statement}` : ''}
                            </div>
                        </div>
                        
                        ${team.members && team.members.length > 0 ? `
                            <div style="border-top: 1px solid #e2e8f0; padding-top: 1rem; margin-top: 1rem;">
                                <strong>Team Members:</strong>
                                <ul style="list-style-type: none; padding-left: 0; margin-top: 0.5rem;">
                                    ${team.members.map(m => `
                                        <li style="margin-bottom: 0.5rem; padding: 0.8rem; background: rgba(0, 212, 255, 0.05); border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.1);">
                                            ${m.name} (${m.email}) - ${m.college}, ${m.department} Year ${m.year}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : '<p style="font-size: 0.9rem; color: #64748b;">No additional members</p>'}
                    </div>
                `).join('');
            }
        } else {
            container.innerHTML = `<p class="empty-state" style="color: var(--error-color);">${data.error || 'Failed to load teams'}</p>`;
        }
    } catch (error) {
        container.innerHTML = '<p class="empty-state" style="color: var(--error-color);">Error loading teams. Please try again.</p>';
    }
}

async function loadExploreHackathons() {
    const container = document.getElementById('hackathons-list');
    container.innerHTML = '<div class="spinner"></div> Loading...';
    
    try {
        const response = await fetch('/api/hackathons');
        if (!response.ok) throw new Error('Failed to load hackathons');
        
        allHackathons = await response.json();
        displayHackathons(allHackathons);
    } catch (error) {
        console.error(error);
        container.innerHTML = '<p class="empty-state">Error loading hackathons. Please try again later.</p>';
    }
}

function displayHackathons(hackathons) {
    const container = document.getElementById('hackathons-list');
    
    if (hackathons.length === 0) {
        container.innerHTML = '<p class="empty-state">No hackathons found.</p>';
        return;
    }
    
    container.innerHTML = hackathons.map(h => `
        <div class="hackathon-card" onclick="viewHackathonDetail(${h.id})">
            <div class="hackathon-poster">
                ${h.poster_url ? `<img src="${h.poster_url}" alt="${h.name}">` : '🚀 ' + h.name.substring(0, 20)}
            </div>
            <div class="hackathon-card-content">
                <h3>${h.name}</h3>
                <div class="hackathon-info">
                    📅 ${formatDate(h.datetime)}
                </div>
                <div class="hackathon-info">
                    📍 ${h.location}
                </div>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                    ${h.description.substring(0, 80)}...
                </p>
                <div class="hackathon-meta">
                    <div class="hackathon-meta-item">
                        👥 Team: ${h.team_size_min}-${h.team_size_max}
                    </div>
                    <div class="hackathon-meta-item">
                        ${h.food_stay_available ? '🍔 Food & Stay' : ''}
                    </div>
                </div>
                ${h.registration_closed ? `
                    <button class="btn" style="width: 100%; background: #e2e8f0; color: #64748b; cursor: not-allowed; padding: 0.8rem; border-radius: 6px; font-weight: 600;" onclick="event.stopPropagation()">
                        Registration Closed
                    </button>
                ` : `
                    <button class="btn btn-primary register-btn" onclick="event.stopPropagation(); openRegistrationModal(${h.id})">
                        Register Now
                    </button>
                `}
            </div>
        </div>
    `).join('');
}

function viewHackathonDetail(hackathonId) {
    const hackathon = allHackathons.find(h => h.id === hackathonId);
    if (!hackathon) return;
    
    currentHackathonId = hackathonId;
    
    const detail = document.getElementById('hackathon-detail');
    detail.innerHTML = `
        <h1>${hackathon.name}</h1>
        
        <div class="detail-section">
            <h2>Overview</h2>
            <div class="detail-row">
                <div class="detail-item">
                    <span class="detail-label">📅 Date & Time</span>
                    <span class="detail-value">${formatDate(hackathon.datetime)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">📍 Location</span>
                    <span class="detail-value">${hackathon.location}</span>
                </div>
            </div>
            <div class="detail-item">
                <span class="detail-label">Description</span>
                <span class="detail-value">${hackathon.description}</span>
            </div>
            <div id="hackathon-map"></div>
        </div>
        
        <div class="detail-section">
            <h2>Organizer Information</h2>
            <div class="detail-row">
                <div class="detail-item">
                    <span class="detail-label">Organizer Name</span>
                    <span class="detail-value">${hackathon.organizer_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Contact Details</span>
                    <span class="detail-value">${hackathon.contact_details}</span>
                </div>
            </div>
        </div>
        
        <div class="detail-section">
            <h2>Prize Pool</h2>
            <div class="detail-item">
                <span class="detail-label">Prize Details</span>
                <span class="detail-value">${hackathon.prize_details}</span>
            </div>
        </div>
        
        <div class="detail-section">
            <h2>Event Structure</h2>
            <div class="detail-row">
                <div class="detail-item">
                    <span class="detail-label">Number of Rounds</span>
                    <span class="detail-value">${hackathon.num_rounds}</span>
                </div>
            </div>
            <div class="detail-item">
                <span class="detail-label">Round Details</span>
                <span class="detail-value">${hackathon.round_details}</span>
            </div>
        </div>
        
        <div class="detail-section">
            <h2>Participation Details</h2>
            <div class="detail-row">
                <div class="detail-item">
                    <span class="detail-label">Problem Statement Type</span>
                    <span class="detail-value">${hackathon.problem_statement_type === 'own' ? 'Own Ideas' : 'Given Problem'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Team Size</span>
                    <span class="detail-value">${hackathon.team_size_min} - ${hackathon.team_size_max} members</span>
                </div>
            </div>
            <div class="detail-item">
                <span class="detail-label">Food & Stay</span>
                <span class="detail-value">${hackathon.food_stay_available ? 'Available ✓' : 'Not Available'}</span>
            </div>
        </div>
        
        <div style="margin-top: 2rem; display: flex; gap: 1rem;">
            ${hackathon.registration_closed ? `
                <button class="btn" style="background: #e2e8f0; color: #64748b; cursor: not-allowed;">Registration Closed</button>
            ` : `
                <button class="btn btn-primary" onclick="openRegistrationModal(${hackathonId})">Register Team</button>
            `}
            <button class="btn btn-secondary" onclick="loadPage('explore')">Back to List</button>
        </div>
    `;
    
    loadPage('hackathon-detail');
    
    setTimeout(() => {
        initializeMap(hackathon.latitude, hackathon.longitude, hackathon.name);
    }, 300);
}

function initializeMap(latitude, longitude, name) {
    const mapElement = document.getElementById('hackathon-map');
    if (!mapElement) return;
    
    mapElement.innerHTML = `
        <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); 
                    height: 300px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    border-radius: 8px; 
                    color: white;
                    font-size: 1.2rem;">
            📍 ${name}<br>
            <small style="font-size: 0.9rem;">Coordinates: ${latitude.toFixed(2)}, ${longitude.toFixed(2)}</small>
        </div>
    `;
}

function openRegistrationModal(hackathonId) {
    currentHackathonId = hackathonId;
    const hackathon = allHackathons.find(h => h.id === hackathonId);
    
    if (!hackathon) return;
    
    teamMemberCount = 0;
    document.getElementById('team-registration-form').reset();
    document.getElementById('team-members-container').innerHTML = '';
    
    if (hackathon.food_stay_available) {
        document.getElementById('food-stay-section').style.display = 'block';
    } else {
        document.getElementById('food-stay-section').style.display = 'none';
    }
    
    if (hackathon.problem_statement_type === 'own') {
        document.getElementById('problem-statement-section').style.display = 'block';
    } else {
        document.getElementById('problem-statement-section').style.display = 'none';
    }
    
    openModal('registration-modal');
}

function addTeamMember() {
    teamMemberCount++;
    const container = document.getElementById('team-members-container');
    
    const memberHtml = `
        <div class="team-member" id="member-${teamMemberCount}">
            <div class="team-member-number">Team Member ${teamMemberCount}</div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" class="member-name" placeholder="Full name" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" class="member-email" placeholder="Email" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Mobile</label>
                    <input type="tel" class="member-mobile" placeholder="Mobile" required>
                </div>
                <div class="form-group">
                    <label>WhatsApp</label>
                    <input type="tel" class="member-whatsapp" placeholder="WhatsApp" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" class="member-dob" required>
                </div>
                <div class="form-group">
                    <label>College/University</label>
                    <input type="text" class="member-college" placeholder="College name" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Degree</label>
                    <input type="text" class="member-degree" placeholder="B.Tech, B.Sc, etc." required>
                </div>
                <div class="form-group">
                    <label>Department</label>
                    <input type="text" class="member-department" placeholder="Department" required>
                </div>
            </div>
            
            <div class="form-group">
                <label>Year</label>
                <select class="member-year" required>
                    <option value="">Select year</option>
                    <option value="I">I</option>
                    <option value="II">II</option>
                    <option value="III">III</option>
                    <option value="IV">IV</option>
                </select>
            </div>
            
            <button type="button" class="remove-member" onclick="removeTeamMember(${teamMemberCount})">Remove Member</button>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', memberHtml);
}

function removeTeamMember(memberId) {
    const member = document.getElementById(`member-${memberId}`);
    if (member) {
        member.remove();
    }
}

async function handleTeamRegistration(event) {
    event.preventDefault();
    
    const teamData = {
        hackathon_id: currentHackathonId,
        team_name: document.getElementById('team-name').value,
        team_members: []
    };
    
    document.querySelectorAll('.team-member').forEach(member => {
        teamData.team_members.push({
            name: member.querySelector('.member-name').value,
            email: member.querySelector('.member-email').value,
            mobile: member.querySelector('.member-mobile').value,
            whatsapp: member.querySelector('.member-whatsapp').value,
            dob: member.querySelector('.member-dob').value,
            college: member.querySelector('.member-college').value,
            degree: member.querySelector('.member-degree').value,
            department: member.querySelector('.member-department').value,
            year: member.querySelector('.member-year').value
        });
    });
    
    const hackathon = allHackathons.find(h => h.id === currentHackathonId);
    if (hackathon.food_stay_available) {
        teamData.food_stay = document.getElementById('food-stay-option').value;
    }
    
    if (hackathon.problem_statement_type === 'own') {
        teamData.problem_statement = document.getElementById('problem-statement').value;
    }
    
    try {
        const response = await fetch('/api/teams', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(teamData)
        });
        
        const data = await response.json();
        if (response.ok) {
            showMessage('Team registered successfully!', 'success');
            setTimeout(() => {
                closeModal('registration-modal');
                loadPage('dashboard');
            }, 1500);
        } else {
            showMessage(data.error || 'Failed to register team', 'error');
        }
    } catch (error) {
        showMessage('Error registering team', 'error');
    }
}

async function handleCreateHackathon(event) {
    event.preventDefault();
    
    const hackathonData = {
        hackathon_name: document.getElementById('h-name').value,
        date_time: document.getElementById('h-datetime').value,
        location: document.getElementById('h-location').value,
        description: document.getElementById('h-description').value,
        organizer_name: document.getElementById('h-organizer').value,
        contact_details: document.getElementById('h-contact').value,
        prize_details: document.getElementById('h-prize').value,
        num_rounds: parseInt(document.getElementById('h-rounds').value),
        round_details: document.getElementById('h-round-details').value,
        problem_statement_type: document.getElementById('h-problem-type').value,
        team_size_min: parseInt(document.getElementById('h-team-min').value),
        team_size_max: parseInt(document.getElementById('h-team-max').value),
        food_stay_available: document.getElementById('h-food-stay').checked,
        poster_url: document.getElementById('h-poster').value || null
    };
    
    try {
        const response = await fetch('/api/hackathons', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(hackathonData)
        });
        
        const data = await response.json();
        if (response.ok) {
            showMessage('Hackathon scheduled successfully!', 'success');
            setTimeout(() => {
                document.getElementById('create-hackathon-form').reset();
                loadPage('dashboard');
            }, 1500);
        } else {
            showMessage(data.error || 'Failed to schedule hackathon', 'error');
        }
    } catch (error) {
        showMessage('Error scheduling hackathon', 'error');
    }
}

function initializeCreateHackathonForm() {
    const form = document.getElementById('create-hackathon-form');
    if (form) {
        form.reset();
    }
}

function filterHackathons(type) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    let filtered = allHackathons;
    if (type === 'upcoming') {
        filtered = allHackathons.filter(h => new Date(h.datetime) > new Date());
    } else if (type === 'completed') {
        filtered = allHackathons.filter(h => new Date(h.datetime) <= new Date());
    }
    
    displayHackathons(filtered);
}

document.addEventListener('keyup', function(event) {
    if (event.target.id === 'search-hackathon') {
        const searchTerm = event.target.value.toLowerCase();
        const filtered = allHackathons.filter(h => 
            h.name.toLowerCase().includes(searchTerm) ||
            h.location.toLowerCase().includes(searchTerm) ||
            h.description.toLowerCase().includes(searchTerm)
        );
        displayHackathons(filtered);
    }
});



async function logout() {
    try {
        await fetch('/logout');
    } catch (e) {}
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userType');
    currentUser = null;
    currentUserType = null;
    updateNavbar();
    loadPage('login');
    document.getElementById('login-form').reset();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

function showMessage(message, type) {
    const modal = document.getElementById('message-modal');
    const messageText = document.getElementById('message-text');
    
    messageText.textContent = message;
    messageText.className = 'alert alert-' + type;
    
    openModal('message-modal');
    
    setTimeout(() => {
        closeModal('message-modal');
    }, 3000);
}

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
});