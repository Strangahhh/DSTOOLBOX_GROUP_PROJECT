document.addEventListener('DOMContentLoaded', (event) => {
    function toggle() {
        let profileDropdownList = document.querySelector(".menu");
        profileDropdownList.classList.toggle("active");
    }

    // Attach the toggle function to the profile element
    let profileElement = document.querySelector(".profile");
    profileElement.addEventListener('click', toggle);
});

