// Бургер меню
const burgerBtn = document.getElementById('burgerBtn');
const sidePanel = document.getElementById('sidePanel');
const overlay = document.getElementById('overlay');
const closeBtn = document.getElementById('closeBtn');
const panelLinks = document.querySelectorAll('.side-panel a');

function toggleMenu() {
    burgerBtn.classList.toggle('active');
    sidePanel.classList.toggle('active');
    overlay.classList.toggle('active');
    document.body.style.overflow = sidePanel.classList.contains('active') ? 'hidden' : '';
}

burgerBtn.addEventListener('click', toggleMenu);
overlay.addEventListener('click', toggleMenu);
closeBtn.addEventListener('click', toggleMenu);

panelLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (sidePanel.classList.contains('active')) {
            toggleMenu();
        }
    });
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// акк пользователя
const userAccountBtn = document.getElementById('userAccountBtn');
const userDropdownMenu = document.getElementById('userDropdownMenu');
const loggedOutView = document.getElementById('loggedOutView');
const loggedInView = document.getElementById('loggedInView');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const logoutBtn = document.getElementById('logoutBtn');

const editProfileLink = document.getElementById('editProfileLink');
const editProfileForm = document.getElementById('editProfileForm');
const editNameInput = document.getElementById('editName');
const editAvatarInput = document.getElementById('editAvatar');
const closeEditProfileBtn = document.querySelector('.close-edit-profile'); // ← КРЕСТИК

const userNameDisplay = document.getElementById('userNameDisplay');
const userAvatarImg = document.querySelector('.user-avatar'); 

const authModal = document.getElementById('authModal');
const closeModalBtn = document.querySelector('.close-modal');

const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const switchToRegister = document.getElementById('switchToRegister');
const switchToLogin = document.getElementById('switchToLogin');

let isLoggedIn = false;
let currentUser = {
    name: 'Гость Бара',
    avatar: null 
};

if (localStorage.getItem('scissors_user')) {
    try {
        const savedData = JSON.parse(localStorage.getItem('scissors_user'));
        isLoggedIn = savedData.isLoggedIn || false;
        currentUser = savedData.currentUser || { name: 'Гость Бара', avatar: null };
    } catch (e) {
        console.error("Ошибка при загрузке данных из localStorage:", e);
        isLoggedIn = false;
        currentUser = { name: 'Гость Бара', avatar: null };
    }
}

function saveToLocalStorage() {
    localStorage.setItem('scissors_user', JSON.stringify({
        isLoggedIn: isLoggedIn,
        currentUser: currentUser
    }));
}

function closeAuthModal() {
    authModal.style.display = 'none';
    document.body.style.overflow = '';
}

function updateUI() {
    if (isLoggedIn) {
        loggedOutView.style.display = 'none';
        loggedInView.style.display = 'block';
        
        if (userNameDisplay) {
            userNameDisplay.textContent = currentUser.name || 'Гость Бара';
        }
        
        if (currentUser.avatar && currentUser.avatar !== '' && currentUser.avatar !== 'null') {
            userAccountBtn.innerHTML = `<img src="${currentUser.avatar}" alt="Аватар" class="user-avatar-small">`;
            userAccountBtn.classList.add('has-avatar');
            
            if (userAvatarImg) {
                userAvatarImg.src = currentUser.avatar;
                userAvatarImg.onerror = function() { this.src = 'https://via.placeholder.com/40'; };
            }

            const btnAvatar = userAccountBtn.querySelector('img');
            if (btnAvatar) {
                btnAvatar.onerror = function() {
                    this.style.display = 'none';
                    userAccountBtn.innerHTML = '<i class="fas fa-user"></i>';
                    userAccountBtn.classList.remove('has-avatar');
                };
            }
        } else {
            userAccountBtn.innerHTML = '<i class="fas fa-user"></i>';
            userAccountBtn.classList.remove('has-avatar');
            
            if (userAvatarImg) {
                userAvatarImg.src = 'https://via.placeholder.com/40';
            }
        }

        const avatarWrapper = document.getElementById('userAvatarWrapper');
        if (avatarWrapper) {
            if (currentUser.avatar && currentUser.avatar !== '' && currentUser.avatar !== 'null') {
                avatarWrapper.innerHTML = `<img src="${currentUser.avatar}" alt="Аватар">`;
                avatarWrapper.classList.add('has-avatar');
            } else {
                avatarWrapper.innerHTML = '<i class="fas fa-user user-avatar-icon"></i>';
                avatarWrapper.classList.remove('has-avatar');
            }
        }

    } else {
        loggedOutView.style.display = 'block';
        loggedInView.style.display = 'none';
        userAccountBtn.innerHTML = '<i class="fas fa-user"></i>';
        userAccountBtn.classList.remove('has-avatar');
        
        const avatarWrapper = document.getElementById('userAvatarWrapper');
        if (avatarWrapper) {
            avatarWrapper.innerHTML = '<i class="fas fa-user user-avatar-icon"></i>';
            avatarWrapper.classList.remove('has-avatar');
        }
    }

    saveToLocalStorage();
}

function activateTab(tabName) {
    const authTabs = document.querySelector('.auth-tabs');
    if (tabName === 'editProfile') {
        authTabs.style.display = 'none';
    } else {
        authTabs.style.display = 'flex';
    }

    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === `${tabName}Tab`) {
            content.classList.add('active');
        }
    });
}

function openEditProfileTab() {
    if (editNameInput) editNameInput.value = currentUser.name || '';
    if (editAvatarInput) editAvatarInput.value = '';
    activateTab('editProfile');
}

if (editProfileLink) {
    editProfileLink.addEventListener('click', (e) => {
        e.preventDefault();
        userDropdownMenu.classList.remove('active');
        authModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        openEditProfileTab();
    });
}

if (closeEditProfileBtn) {
    closeEditProfileBtn.addEventListener('click', () => {
        closeAuthModal();
    });
}

if (editProfileForm) {
    editProfileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const newName = editNameInput.value.trim();
        if (newName !== '') currentUser.name = newName;
        
        if (editAvatarInput && editAvatarInput.files && editAvatarInput.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                currentUser.avatar = e.target.result;
                updateUI();
                closeAuthModal();
            };
            reader.readAsDataURL(editAvatarInput.files[0]);
        } else {
            currentUser.avatar = null;
            updateUI();
            closeAuthModal();
        }
    });
}

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        activateTab(tabName);
    });
});

if (switchToRegister) {
    switchToRegister.addEventListener('click', (e) => {
        e.preventDefault();
        activateTab('register');
    });
}

if (switchToLogin) {
    switchToLogin.addEventListener('click', (e) => {
        e.preventDefault();
        activateTab('login');
    });
}

userAccountBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    
    if (!isLoggedIn) {
        authModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        activateTab('login');
    } else {
        userDropdownMenu.classList.toggle('active');
    }
});

document.addEventListener('click', (e) => {
    if (!userDropdownMenu.contains(e.target) && !userAccountBtn.contains(e.target)) {
        userDropdownMenu.classList.remove('active');
    }
});

document.querySelector('#loggedOutView .dropdown-link').addEventListener('click', (e) => {
    e.preventDefault();
    userDropdownMenu.classList.remove('active');
    authModal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    activateTab('login');
});

closeModalBtn.addEventListener('click', () => {
    closeAuthModal();
});

window.addEventListener('click', (e) => {
    if (e.target === authModal) {
        closeAuthModal();
    }
});

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    isLoggedIn = true;
    updateUI();
    loginForm.reset();
    closeAuthModal();
});

registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const regNameInput = document.getElementById('regName');
    if (regNameInput && regNameInput.value.trim() !== '') {
        currentUser.name = regNameInput.value.trim();
    }
    
    isLoggedIn = true;
    updateUI();
    registerForm.reset();
    closeAuthModal();
});

logoutBtn.addEventListener('click', (e) => {
    e.preventDefault();
    isLoggedIn = false;
    currentUser = { name: 'Гость Бара', avatar: null };
    updateUI();
    
    // Очищаем формы
    if (loginForm) loginForm.reset();
    if (registerForm) registerForm.reset();
    if (editProfileForm) editProfileForm.reset();

    userDropdownMenu.classList.remove('active');
});

updateUI();