/* =====================================================
   GALINDO FIT - MAIN JS
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       LOGIN
    ===================================================== */

    const loginForm = document.getElementById("loginForm");

    if (loginForm) {

        const passwordInput = document.getElementById("password");

        const jsAlert = document.getElementById("js-alert");

        loginForm.addEventListener("submit", (e) => {

            jsAlert.classList.add("d-none");

            jsAlert.textContent = "";

            const password = passwordInput.value.trim();

            // Campo vacío
            if (password === "") {

                e.preventDefault();

                jsAlert.textContent =
                    "El código de acceso no puede estar vacío.";

                jsAlert.classList.remove("d-none");

                passwordInput.focus();

                return;
            }

            // Muy corto
            if (password.length < 4) {

                e.preventDefault();

                jsAlert.textContent =
                    "Código demasiado corto.";

                jsAlert.classList.remove("d-none");

                passwordInput.focus();

                return;
            }

        });

    }

    /* =====================================================
       REGISTRO
    ===================================================== */

    const registroForm = document.getElementById("registroForm");

    if (registroForm) {

        const nombre = document.getElementById("nombre");

        const email = document.getElementById("email");

        const alertBox = document.getElementById("js-alert");

        registroForm.addEventListener("submit", (e) => {

            alertBox.classList.add("d-none");

            alertBox.textContent = "";

            // Nombre válido
            if (nombre.value.trim().length < 3) {

                e.preventDefault();

                alertBox.textContent =
                    "El nombre debe tener mínimo 3 caracteres.";

                alertBox.classList.remove("d-none");

                nombre.focus();

                return;
            }

            // Email simple
            if (!email.value.includes("@")) {

                e.preventDefault();

                alertBox.textContent =
                    "Ingresa un correo válido.";

                alertBox.classList.remove("d-none");

                email.focus();

                return;
            }

        });

    }

    /* =====================================================
       EFECTO NAVBAR SCROLL
    ===================================================== */

    const navbar = document.querySelector(".navbar");

    if (navbar) {

        window.addEventListener("scroll", () => {

            if (window.scrollY > 50) {

                navbar.style.background = "rgba(10,10,11,.92)";

                navbar.style.backdropFilter = "blur(10px)";

                navbar.style.transition = "all .3s ease";

            } else {

                navbar.style.background = "transparent";

                navbar.style.backdropFilter = "blur(0px)";

            }

        });

    }

    /* =====================================================
       ANIMACIÓN SCROLL SUAVE
    ===================================================== */

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {

        anchor.addEventListener("click", function (e) {

            e.preventDefault();

            const target = document.querySelector(this.getAttribute("href"));

            if (target) {

                target.scrollIntoView({
                    behavior: "smooth"
                });

            }

        });

    });

    /* =====================================================
       NAVBAR RESPONSIVE TOGGLE
    ===================================================== */
    const navToggle = document.getElementById("navToggle");
    const navMenu = document.getElementById("navMenu");
    
    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            navMenu.classList.toggle("active");
        });
    }

});