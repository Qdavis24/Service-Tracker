function toggleModal(state) {
        const loginModal = document.getElementById('login-modal');
        const registerModal = document.getElementById('register-modal');
        if (state === 0) {
            loginModal.style.display = 'none';
            registerModal.style.display = 'none';
        } else if (state === 1) {
            registerModal.style.display = 'none';
            loginModal.style.display = 'flex';
        } else if (state === 2) {
            loginModal.style.display = 'none';
            registerModal.style.display = 'flex';

        }
    }