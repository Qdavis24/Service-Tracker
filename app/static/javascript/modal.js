function toggleModal(state, m1, m2) {

        if (state === 0) {
            m1.style.display = 'none';
            m2.style.display = 'none';
        } else if (state === 1) {
            m1.style.display = 'flex';
            m2.style.display = 'none';
        } else if (state === 2) {
            m1.style.display = 'none';
            m2.style.display = 'flex';

        }
    }