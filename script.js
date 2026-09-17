/* ========================================
   UNJED-BENIN - Scripts partages
   Mode sombre, traduction FR/EN, menu mobile,
   cookies, reveal au scroll, formulaires
   ======================================== */

(function () {
  "use strict";

  /* ---------- 1. Mode sombre ---------- */
  const root = document.documentElement;
  const storedTheme = localStorage.getItem("unjed-theme");
  if (storedTheme === "dark") root.setAttribute("data-theme", "dark");

  function toggleTheme() {
    const isDark = root.getAttribute("data-theme") === "dark";
    if (isDark) {
      root.removeAttribute("data-theme");
      localStorage.setItem("unjed-theme", "light");
    } else {
      root.setAttribute("data-theme", "dark");
      localStorage.setItem("unjed-theme", "dark");
    }
  }

  /* ---------- 2. Traduction FR / EN ---------- */
  // On stocke le texte FR original dans data-fr au premier passage,
  // puis on remplace par data-en. Les elements traduisibles ont [data-en].
  const storedLang = localStorage.getItem("unjed-lang") || "fr";

  function applyLang(lang) {
    document.querySelectorAll("[data-en]").forEach((el) => {
      if (!el.hasAttribute("data-fr")) {
        el.setAttribute("data-fr", el.innerHTML);
      }
      el.innerHTML = lang === "en" ? el.getAttribute("data-en") : el.getAttribute("data-fr");
    });
    // Attributs traduisibles (placeholder)
    document.querySelectorAll("[data-en-placeholder]").forEach((el) => {
      if (!el.hasAttribute("data-fr-placeholder")) {
        el.setAttribute("data-fr-placeholder", el.getAttribute("placeholder") || "");
      }
      el.setAttribute(
        "placeholder",
        lang === "en" ? el.getAttribute("data-en-placeholder") : el.getAttribute("data-fr-placeholder")
      );
    });
    root.setAttribute("lang", lang);
    localStorage.setItem("unjed-lang", lang);
    document.querySelectorAll(".lang-current").forEach((s) => {
      s.textContent = lang === "en" ? "EN" : "FR";
    });
  }

  function toggleLang() {
    const current = localStorage.getItem("unjed-lang") || "fr";
    applyLang(current === "fr" ? "en" : "fr");
  }

  /* ---------- 3. Menu mobile ---------- */
  function setupMobileMenu() {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".main-nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", () => {
      nav.classList.toggle("open");
      const open = nav.classList.contains("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => nav.classList.remove("open"))
    );
  }

  const slides = document.querySelectorAll('.hero-slide');
  const dots = document.querySelectorAll('.hero-dot');
  if (slides.length > 0) {
    let current = 0;
    let timer;
    const show = (idx) => {
      slides[current].classList.remove('active');
      dots[current]?.classList.remove('active');
      current = (idx + slides.length) % slides.length;
      slides[current].classList.add('active');
      dots[current]?.classList.add('active');
    };
    const next = () => show(current + 1);
    const startTimer = () => { timer = setInterval(next, 3000); };
    startTimer();
    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => { clearInterval(timer); show(i); startTimer(); });
    });
  }

  /* ---------- 4. Banniere cookies ---------- */
  function setupCookies() {
  function attachCookie() {
    const banner = document.querySelector(".cookie-banner");
    if (!banner) return false;
    if (sessionStorage.getItem("unjed-cookie-ack")) return true;
    setTimeout(() => banner.classList.add("show"), 900);
    banner.querySelectorAll("[data-cookie-close]").forEach((btn) =>
      btn.addEventListener("click", () => {
        sessionStorage.setItem("unjed-cookie-ack", "1");
        banner.classList.remove("show");
      })
    );
    return true;
  }
  if (!attachCookie()) {
    const tid = setInterval(() => {
      if (attachCookie()) clearInterval(tid);
    }, 100);
    setTimeout(() => clearInterval(tid), 3000);
  }
}
  /* ---------- 5. Reveal au scroll ---------- */
  function setupReveal() {
    const els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window) || !els.length) {
      els.forEach((el) => el.classList.add("in"));
      return;
    }
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    els.forEach((el) => obs.observe(el));
  }

  /* ---------- 6. Active link highlight ---------- */
  function setupActiveLink() {
    const path = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".main-nav a").forEach((a) => {
      const href = a.getAttribute("href");
      if (href === path || (path === "" && href === "index.html")) {
        a.classList.add("active");
      }
    });
  }

  /* ---------- 7. Voir plus / Voir moins membres ---------- */
  function setupSeeMore() {
    document.querySelectorAll(".member-see-more").forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-target");
        const expand = document.getElementById(targetId);
        if (!expand) return;
        const isOpen = !expand.hidden;
        if (isOpen) {
          // Fermer
          expand.classList.remove("open");
          setTimeout(() => { expand.hidden = true; }, 350);
          btn.classList.remove("expanded");
          btn.innerHTML = 'Voir plus <span class="see-more-arrow">&#8595;</span>';
          btn.setAttribute("aria-expanded", "false");
        } else {
          // Ouvrir
          expand.hidden = false;
          // forcer reflow
          expand.offsetHeight;
          expand.classList.add("open");
          btn.classList.add("expanded");
          btn.innerHTML = 'Voir moins <span class="see-more-arrow">&#8595;</span>';
          btn.setAttribute("aria-expanded", "true");
          // Scroll doux vers la carte
          const scrollTarget = btn.closest(".member-card") || btn.closest(".see-more-block") || btn;
          scrollTarget.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      });
    });
  }

  /* ---------- 7. Formulaires (demo, sans backend) ---------- */
  function setupForms() {
    const forms = document.querySelectorAll(
      "form[data-demo-form], #membership-form, #contact-form, #newsletter-form"
    );
    forms.forEach((form) => {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const success =
          form.querySelector(".form-success") ||
          form.parentElement.querySelector(".form-success");
        if (success) {
          success.hidden = false;
          success.classList.add("show");
          success.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        form.reset();
      });
    });
  }

  /* ---------- Header scrolled state (bordure/ombre uniquement au défilement) ---------- */
  function setupHeaderScroll() {
    const header = document.querySelector(".site-header");
    if (!header) return;
    const onScroll = () => {
      header.classList.toggle("scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- Init ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-theme-toggle]").forEach((b) =>
      b.addEventListener("click", toggleTheme)
    );
    document.querySelectorAll("[data-lang-toggle]").forEach((b) =>
      b.addEventListener("click", toggleLang)
    );
    setupMobileMenu();
    setupCookies();
    setupReveal();
    setupActiveLink();
    setupForms();
    setupSeeMore();
    setupHeaderScroll();
    if (storedLang === "en") applyLang("en");
    else applyLang("fr");
  });
})();
