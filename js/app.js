/* =========================
   Dark Mode Toggle
   Persists preference via localStorage
   ========================= */

   // this runs immediately so nothing leaks outside of it
(function () {
    // gets whatever theme was saved before
    const savedTheme = localStorage.getItem('theme');
    // checks if the user's computer is already set to dark mode
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add('dark-mode');
    }

    document.addEventListener('DOMContentLoaded', function () {
        const nav = document.querySelector('nav');

        // ── Dark Mode Toggle ──
        // makes the dark mode button
        const toggle = document.createElement('button');
        toggle.id = 'dark-mode-toggle';
        // accessibility label (for screen readers)
        toggle.setAttribute('aria-label', 'Toggle dark mode');
        toggle.title = 'Toggle dark mode';

        // sets the icon based on current theme
        updateIcon(toggle);

        // Insert into the page (inside <nav> if it exists, otherwise top of <body>)
        if (nav) {
            nav.appendChild(toggle);
        } else {
            document.body.prepend(toggle);
        }

        // Toggle on click
        toggle.addEventListener('click', function () {
            // adds or removes the dark-mode class
            document.documentElement.classList.toggle('dark-mode');
            const isDark = document.documentElement.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            // updates the icon after switching
            updateIcon(toggle);
        });

        // ── Hamburger Menu ──
        if (nav) {
            // Wrap loose <a> tags (lab pages) in a .nav-links container
            // so CSS can show/hide them the same way it does with <ul>
            if (!nav.querySelector('ul')) {
                // grabs only direct <a> children inside nav
                const links = Array.from(nav.querySelectorAll(':scope > a'));
                if (links.length) {
                    // makes a wrapper div for those links
                    const wrapper = document.createElement('div');
                    wrapper.className = 'nav-links';
                    // moves each link into the wrapper
                    links.forEach(function (link) { wrapper.appendChild(link); });
                    // insert wrapper at the start of nav (before toggle)
                    nav.prepend(wrapper);
                }
            }

            // Create hamburger button
            const hamburger = document.createElement('button');
            hamburger.id = 'hamburger-toggle';
            hamburger.setAttribute('aria-label', 'Open navigation menu');
            hamburger.setAttribute('aria-expanded', 'false');
            hamburger.innerHTML = '&#9776;'; // ☰ icon
            // puts the hamburger at the very top of nav
            nav.prepend(hamburger);

            // when clicked, open or close the menu
            hamburger.addEventListener('click', function () {
                // toggles the nav-open class
                nav.classList.toggle('nav-open');
                // checks if it’s currently open
                const isOpen = nav.classList.contains('nav-open');
                // updates accessibility attribute
                hamburger.setAttribute('aria-expanded', isOpen);
                // switches icon between ☰ and ✕
                hamburger.innerHTML = isOpen ? '&times;' : '&#9776;';
            });

            // Close the menu when a nav link is clicked (nice UX on mobile)
            nav.addEventListener('click', function (e) {
                if (e.target.tagName === 'A') {
                    nav.classList.remove('nav-open');
                    hamburger.setAttribute('aria-expanded', 'false');
                    hamburger.innerHTML = '&#9776;';
                }
            });
        }
    });

    // if a link inside nav is clicked,
    // automatically close the menu (better for mobile)
    function updateIcon(btn) {
        const isDark = document.documentElement.classList.contains('dark-mode');
        // if dark mode is on → sun icon, otherwise moon
        btn.textContent = isDark ? '☀️' : '🌙';
    }
})();
