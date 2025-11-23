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
    
    function closeMobileMenu() {
        sidebar.classList.remove('active');
        if (mobileOverlay) {
            mobileOverlay.classList.remove('active');
        }

        // Reset hamburger icon
        if (menuToggle) {
            const spans = menuToggle.querySelectorAll('span');
            if (spans.length >= 3) {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        }
    }
    
    function openMobileMenu() {
        sidebar.classList.add('active');
        if (mobileOverlay) {
            mobileOverlay.classList.add('active');
        }
        
        // Animate hamburger icon
        const spans = menuToggle.querySelectorAll('span');
        spans[0].style.transform = 'rotate(45deg) translate(8px, 8px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(7px, -7px)';
    }
    
    console.log('Main.js: menuToggle', !!menuToggle, 'sidebar', !!sidebar, 'mainContent', !!mainContent);
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            if (sidebar.classList.contains('active')) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
        });
        
        // Close menu when clicking overlay
        if (mobileOverlay) {
            mobileOverlay.addEventListener('click', function() {
                closeMobileMenu();
            });
        }
        
        // Close sidebar when clicking outside on mobile
        mainContent.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                    closeMobileMenu();
                }
            }
        });
        
        // Close menu when clicking a regular menu link (not submenu parent)
        const menuLinks = sidebar.querySelectorAll('.menu-link');
        console.log('Main.js: found menuLinks', menuLinks.length);
        menuLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Only close if it's not a submenu parent
                const menuItem = this.closest('.menu-item');
                if (window.innerWidth <= 768 && !menuItem.classList.contains('has-submenu')) {
                    closeMobileMenu();
                }
            });
        });
        
        // Close menu when clicking a submenu link
        const submenuLinks = sidebar.querySelectorAll('.submenu-link');
        console.log('Main.js: found submenuLinks', submenuLinks.length);
        submenuLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    closeMobileMenu();
                }
            });
        });
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
