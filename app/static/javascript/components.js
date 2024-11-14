function addFlashMessage(msg) {
    const flashContainer = document.getElementById('flash-container');
    const newFlash = document.createElement('li');
    newFlash.innerHTML = msg;
    newFlash.className = 'animate-flash flash-message w-full';
    flashContainer.appendChild(newFlash);
}