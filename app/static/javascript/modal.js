function toggleModal(state, m1, m2) {

        if (state === 0) {
            m1.style.display = 'none';
            m2.style.display = 'none';
        } else if (state === 1) {
            m2.style.display = 'none';
            m1.style.display = 'flex';
        } else if (state === 2) {
            m1.style.display = 'none';
            m2.style.display = 'flex';

        }
    }