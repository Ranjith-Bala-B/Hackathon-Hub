import sys

with open('script.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace handleLogin
content = content.replace('''function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    if (!email || !password) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    const mockUser = {
        id: 1,
        email: email,
        name: email.split('@')[0]
    };
    
    let userType = 'student';
    if (email.includes('org') || email.includes('organization')) {
        userType = 'organization';
    }
    
    currentUser = mockUser;
    currentUserType = userType;
    
    localStorage.setItem('currentUser', JSON.stringify(mockUser));
    localStorage.setItem('userType', userType);
    
    updateNavbar();
    showMessage('Login successful!', 'success');
    
    setTimeout(() => {
        loadPage('dashboard');
    }, 1000);
}''', '''async function handleLogin(event) {
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
}''')

# Replace handleSignup
content = content.replace('''function handleSignup(event) {
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
        const confirmPassword = document.getElementById('student-confirm-password').value;
        
        if (userData.password !== confirmPassword) {
            showMessage('Passwords do not match', 'error');
            return;
        }
    } else {
        userData.organization_name = document.getElementById('org-name').value;
        userData.phone = document.getElementById('org-phone').value;
        userData.email = document.getElementById('org-email').value;
        userData.address = document.getElementById('org-address').value;
        userData.password = document.getElementById('org-password').value;
        const confirmPassword = document.getElementById('org-confirm-password').value;
        
        if (userData.password !== confirmPassword) {
            showMessage('Passwords do not match', 'error');
            return;
        }
    }
    
    const newUser = {
        id: Math.random(),
        email: userData.email,
        name: userData.name || userData.organization_name
    };
    
    showMessage('Signup successful! Please login.', 'success');
    
    setTimeout(() => {
        document.getElementById('signup-form').reset();
        loadPage('login');
    }, 1500);
}''', '''async function handleSignup(event) {
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
}''')

# Replace loadDashboard
content = content.replace('''function loadDashboard() {
    const studentDashboard = document.getElementById('student-dashboard');
    const orgDashboard = document.getElementById('organization-dashboard');
    
    if (currentUserType === 'student') {
        studentDashboard.style.display = 'block';
        orgDashboard.style.display = 'none';
        loadStudentDashboard();
    } else {
        studentDashboard.style.display = 'none';
        orgDashboard.style.display = 'block';
        loadOrgDashboard();
    }
    
    document.getElementById('user-name').textContent = currentUser.name;
}''', '''async function loadDashboard() {
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
}''')

# Replace loadStudentDashboard
content = content.replace('''function loadStudentDashboard() {
    const list = document.getElementById('student-registered-list');
    
    const registeredHackathons = [];
    
    if (registeredHackathons.length === 0) {
        list.innerHTML = '<p class="empty-state">No hackathons registered yet. <a href="#" onclick="loadPage(\\'explore\\')" style="color: var(--primary-color);">Explore hackathons</a></p>';
    } else {
        list.innerHTML = registeredHackathons.map(h => `
            <div class="scheduled-item">
                <h4>${h.name}</h4>
                <p>📅 ${h.datetime}</p>
                <p>📍 ${h.location}</p>
            </div>
        `).join('');
    }
}''', '''function loadStudentDashboard(registeredHackathons) {
    const list = document.getElementById('student-registered-list');
    
    if (!registeredHackathons || registeredHackathons.length === 0) {
        list.innerHTML = '<p class="empty-state">No hackathons registered yet. <a href="#" onclick="loadPage(\\'explore\\')" style="color: var(--primary-color);">Explore hackathons</a></p>';
    } else {
        list.innerHTML = registeredHackathons.map(h => `
            <div class="scheduled-item">
                <h4>${h.name}</h4>
                <p>📅 ${formatDate(h.datetime)}</p>
                <p>📍 ${h.location}</p>
            </div>
        `).join('');
    }
}''')

# Replace loadOrgDashboard
content = content.replace('''function loadOrgDashboard() {
    const list = document.getElementById('org-scheduled-list');
    
    const scheduledHackathons = [];
    
    if (scheduledHackathons.length === 0) {
        list.innerHTML = '<p class="empty-state">No hackathons scheduled yet. <a href="#" onclick="loadPage(\\'create-hackathon\\')" style="color: var(--primary-color);">Create your first hackathon</a></p>';
    } else {
        list.innerHTML = scheduledHackathons.map(h => `
            <div class="scheduled-item">
                <h4>${h.name}</h4>
                <p>📅 ${h.datetime}</p>
                <p>📍 ${h.location}</p>
                <p>Registered Teams: ${h.teams || 0}</p>
            </div>
        `).join('');
    }
}''', '''function loadOrgDashboard(scheduledHackathons) {
    const list = document.getElementById('org-scheduled-list');
    
    if (!scheduledHackathons || scheduledHackathons.length === 0) {
        list.innerHTML = '<p class="empty-state">No hackathons scheduled yet. <a href="#" onclick="loadPage(\\'create-hackathon\\')" style="color: var(--primary-color);">Create your first hackathon</a></p>';
    } else {
        list.innerHTML = scheduledHackathons.map(h => `
            <div class="scheduled-item">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <h4>${h.name}</h4>
                    <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.8rem; background: #fee2e2; color: #dc2626; border-color: #fca5a5;" onclick="deleteHackathon(${h.id})">Delete</button>
                </div>
                <p>📅 ${formatDate(h.datetime)}</p>
                <p>📍 ${h.location}</p>
                <p>Registered Teams: ${h.teams || 0}</p>
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
}''')

# Replace loadExploreHackathons (the long one)
content = content.replace('''function loadExploreHackathons() {
    const container = document.getElementById('hackathons-list');
    container.innerHTML = '<div class="spinner"></div> Loading...';
    
    allHackathons = [
        {
            id: 1,
            name: 'Tech Innovation Hackathon 2024',
            datetime: '2024-05-15 09:00',
            location: 'Bangalore, India',
            latitude: 12.9716,
            longitude: 77.5946,
            description: 'A 24-hour hackathon focused on AI and Machine Learning innovations.',
            organizer_name: 'Tech Hub India',
            contact_details: '+91-8800123456, contact@techhub.in',
            prize_details: '₹1,00,000 for 1st place, ₹50,000 for 2nd, ₹25,000 for 3rd',
            num_rounds: 3,
            round_details: 'Round 1: Idea Pitching, Round 2: Development, Round 3: Final Presentation',
            problem_statement_type: 'given',
            team_size_min: 2,
            team_size_max: 4,
            food_stay_available: true,
            poster_url: '',
            organization_name: 'Tech Hub India'
        },
        {
            id: 2,
            name: 'Web Development Championship',
            datetime: '2024-06-20 10:00',
            location: 'Mumbai, India',
            latitude: 19.0760,
            longitude: 72.8777,
            description: 'A hackathon for web developers to showcase their skills in building innovative web solutions.',
            organizer_name: 'Web Developers Association',
            contact_details: '+91-9900123456, info@webdevassoc.com',
            prize_details: '₹75,000 for winners + sponsorship deals',
            num_rounds: 2,
            round_details: 'Round 1: Coding Phase (12 hours), Round 2: Presentation & Judging',
            problem_statement_type: 'own',
            team_size_min: 1,
            team_size_max: 3,
            food_stay_available: false,
            poster_url: '',
            organization_name: 'Web Developers Association'
        },
        {
            id: 3,
            name: 'Mobile App Innovation Challenge',
            datetime: '2024-07-10 08:00',
            location: 'Hyderabad, India',
            latitude: 17.3850,
            longitude: 78.4867,
            description: 'Build the next breakthrough mobile application in this 48-hour hackathon.',
            organizer_name: 'Mobile Dev Forum',
            contact_details: '+91-7700123456, hello@mobiledevforum.in',
            prize_details: '₹2,00,000 total prize pool',
            num_rounds: 3,
            round_details: 'Screening, Development, Final Demo',
            problem_statement_type: 'own',
            team_size_min: 2,
            team_size_max: 5,
            food_stay_available: true,
            poster_url: '',
            organization_name: 'Mobile Dev Forum'
        }
    ];
    
    displayHackathons(allHackathons);
}''', '''async function loadExploreHackathons() {
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
}''')

# Replace handleTeamRegistration
content = content.replace('''function handleTeamRegistration(event) {
    event.preventDefault();
    
    const teamData = {
        hackathon_id: currentHackathonId,
        team_name: document.getElementById('team-name').value,
        team_leader: {
            name: document.getElementById('leader-name').value,
            email: document.getElementById('leader-email').value,
            mobile: document.getElementById('leader-mobile').value,
            whatsapp: document.getElementById('leader-whatsapp').value,
            dob: document.getElementById('leader-dob').value,
            college: document.getElementById('leader-college').value,
            degree: document.getElementById('leader-degree').value,
            department: document.getElementById('leader-department').value,
            year: document.getElementById('leader-year').value
        },
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
    
    console.log('Team Registration Data:', teamData);
    showMessage('Team registered successfully!', 'success');
    
    setTimeout(() => {
        closeModal('registration-modal');
        loadPage('dashboard');
    }, 1500);
}''', '''async function handleTeamRegistration(event) {
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
}''')

# Replace handleCreateHackathon
content = content.replace('''function handleCreateHackathon(event) {
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
    
    console.log('Hackathon Data:', hackathonData);
    showMessage('Hackathon scheduled successfully!', 'success');
    
    setTimeout(() => {
        document.getElementById('create-hackathon-form').reset();
        loadPage('dashboard');
    }, 1500);
}''', '''async function handleCreateHackathon(event) {
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
}''')

# Replace logout
content = content.replace('''function logout() {
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userType');
    currentUser = null;
    currentUserType = null;
    updateNavbar();
    loadPage('login');
    document.getElementById('login-form').reset();
}''', '''async function logout() {
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
}''')

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(content)
