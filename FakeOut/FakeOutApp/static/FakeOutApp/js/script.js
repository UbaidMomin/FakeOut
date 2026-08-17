// ==========================================================================
// FakeOut - script.js
// ==========================================================================

document.addEventListener('DOMContentLoaded', function () {
    initMobileNav();
    initContactFormValidation();
    initAutoDismissMessages();
});

/**
 * Toggles the mobile navigation menu open/closed.
 */
function initMobileNav() {
    var toggle = document.getElementById('navToggle');
    var nav = document.getElementById('mainNav');

    if (!toggle || !nav) {
        return;
    }

    toggle.addEventListener('click', function () {
        var isOpen = nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close the menu when a nav link is clicked (mobile UX).
    nav.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            nav.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
        });
    });
}

/**
 * Lightweight client-side validation for the contact form.
 * Server-side validation in the Django view is still the source of truth.
 */
function initContactFormValidation() {
    var form = document.querySelector('.contact-form');
    if (!form) {
        return;
    }

    form.addEventListener('submit', function (event) {
        var name = form.querySelector('#id_name');
        var email = form.querySelector('#id_email');
        var message = form.querySelector('#id_message');
        var isValid = true;

        [name, email, message].forEach(function (field) {
            if (field && !field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#dc2626';
            } else if (field) {
                field.style.borderColor = '';
            }
        });

        if (!isValid) {
            event.preventDefault();
        }
    });

    // Clear the red border as soon as the user starts typing again.
    form.querySelectorAll('input, textarea').forEach(function (field) {
        field.addEventListener('input', function () {
            field.style.borderColor = '';
        });
    });
}

/**
 * Auto-dismisses success/error alert banners after a few seconds.
 */
function initAutoDismissMessages() {
    var alerts = document.querySelectorAll('.alert');
    if (!alerts.length) {
        return;
    }

    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 4000);
    });
}

// ---------- Analyze form (home page) ----------
// No analysis backend is wired up yet — this keeps the button from
// silently reloading the page with no feedback. Replace this with a
// real fetch() call to your analyze view/API when it's ready.
document.addEventListener('DOMContentLoaded', function () {
    var analyzeForm = document.querySelector('.analyze-form');
    if (!analyzeForm) {
        return;
    }

    analyzeForm.addEventListener('submit', function (event) {
        var input = analyzeForm.querySelector('input[name="url"]');
        if (!input || !input.value.trim()) {
            event.preventDefault();
            return;
        }
        // TODO: hook this up to a real /analyze/ endpoint.
        event.preventDefault();
        alert('Analyze feature coming soon for: ' + input.value.trim());
    });
});

/**
 * Toggles password field visibility (show/hide) and swaps eye icons.
 */
document.addEventListener('DOMContentLoaded', function () {
    var toggleButtons = document.querySelectorAll('.password-toggle');

    toggleButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var wrapper = btn.closest('.password-wrapper');
            var input = wrapper.querySelector('input');
            var eyeIcon = btn.querySelector('.eye-icon');
            var eyeOffIcon = btn.querySelector('.eye-off-icon');

            if (input.type === 'password') {
                input.type = 'text';
                eyeIcon.style.display = 'none';
                eyeOffIcon.style.display = 'block';
            } else {
                input.type = 'password';
                eyeIcon.style.display = 'block';
                eyeOffIcon.style.display = 'none';
            }
        });
    });
});