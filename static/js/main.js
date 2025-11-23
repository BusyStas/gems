/**
 * Gems Hub - Main JavaScript
 * Handles menu interactions and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Menu toggle functionality
    // Support multiple possible IDs for the menu toggle to match the template
    const menuToggle = document.getElementById('menu-toggle') || document.getElementById('menuToggle') || document.querySelector('.menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    function closeMobileMenu(reason) {
        console.log('closeMobileMenu called:', reason || 'unknown');
        sidebar.classList.remove('active');
        if (mobileOverlay) {
            mobileOverlay.classList.remove('active');
        }
        // Keep hamburger icon as default sandwich - do not transform to cross
    }
    
    function openMobileMenu() {
        console.log('openMobileMenu called');
        sidebar.classList.add('active');
        if (mobileOverlay) {
            mobileOverlay.classList.add('active');
        }
        // Keep hamburger icon as default sandwich - do not transform to cross
    }
    
    console.log('Main.js: menuToggle', !!menuToggle, 'sidebar', !!sidebar, 'mainContent', !!mainContent);
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            if (sidebar.classList.contains('active')) {
                closeMobileMenu('menuToggle click - close');
            } else {
                openMobileMenu();
            }
        });
        
        // Close menu when clicking overlay
        if (mobileOverlay) {
            mobileOverlay.addEventListener('click', function() {
                closeMobileMenu('mobileOverlay click');
            });
        }
        
        // Close sidebar when clicking outside on mobile
        mainContent.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                    closeMobileMenu('mainContent click outside');
                }
            }
        });
        
        // Navigation clicks on menu items are handled in the side_menu.js delegation
    }
    
    // Submenu hover/tap handling is performed by side_menu.js (delegation)
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Close mobile menu when resizing to desktop
            if (window.innerWidth > 768 && sidebar && sidebar.classList.contains('active')) {
                closeMobileMenu();
            }
        }, 250);
    });
});
