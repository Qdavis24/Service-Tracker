// sets a single element to a specified opacity
function setOpacity(el, value, time) {
    el.style.transition = `opacity ${time}s ease-in-out`;
    el.style.opacity = value;
}

// takes the element that should be visible and sets all siblings to invisible
function setOpacities(el, time) {
    setOpacity(el, 1);
    [...el.parentElement.children] // spread operator to convert element collection into iterable array
        .filter(sibling => sibling !== el) // only keep elements that are not the current center element
        .forEach(s => setOpacity(s, 0, time)); // set all elements left to 0 opacity
}

// if the last element is above or at center change ui to show up arrow
// else show down arrow
function toggleArrowVis(mWH, scrollUp, scrollDown, lastScroll) {

    let lastScrollRect = lastScroll.getBoundingClientRect();

    if (lastScrollRect.top <= mWH) {
        setOpacity(scrollUp, 1);
        setOpacity(scrollDown, 0);
    } else {
        setOpacity(scrollDown, 1);
        setOpacity(scrollUp, 0);

    }
}

// check each element for distance form center
// if it is closer than last closest reset closest and least distance
function retrieveClosest(mWH) {
    const elements = document.querySelectorAll('.scroll-fade');
    let closest = null;
    let leastDistance = Infinity;
    elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        let distanceFromCenter = Math.abs((rect.top + rect.height / 2) - mWH);
        if (distanceFromCenter < leastDistance) {
            leastDistance = distanceFromCenter;
            closest = el;
        }
    });
    return closest;
}

// use direction to find the next element in the parent
function findNext(closest, direction) {
    let next = null;
    if (direction === "down") {
        next = closest.nextElementSibling;
    } else {
        next = closest.previousElementSibling;
    }
    return next;
}

// scroll element into view smoothly to block center -> vertical center & inline center -> horizontal center
function centerElement(el) {
    el.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'center',
    })

}

function handleScroll(mWH, direction) {
    const last = document.getElementById('dummy');
    let el = retrieveClosest(mWH); // retrieve the center most element
    el = findNext(el, direction) // find the next element to be scrolled into view based on direction of scroll
    if (!el || el === last) return; // if there is no next element IE last element in parent with down scroll early return
    setOpacities(el, .3);
    centerElement(el); // move to be scrolled to center


}
