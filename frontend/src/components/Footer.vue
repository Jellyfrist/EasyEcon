<template>
    <footer class="footer">
        <div class="container">
    
            <!-- Top Section -->
            <div class="footer-top">
    
                <!-- Logo -->
                <div class="logo">Easy<span class="text-pink">Econ</span></div>
    
                <!-- Navigation -->
                <nav class="nav">
                    <a v-for="item in links" :key="item" href="#" class="nav-link">
                    {{ item }}
                </a>
                </nav>
    
                <!-- Language Icon -->
                <div class="language">
                    <span class="material-symbols-outlined">language</span>
                </div>
    
            </div>
    
            <!-- Bottom Section -->
            <div class="footer-bottom">
                <p>
                    © {{ currentYear }} EASY ECON. All rights reserved. Built for future economists.
                </p>
            </div>
    
        </div>
    </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()

const links = [
    "About Us",
    "Help Center",
    "Privacy",
    "Terms"
]
</script>

<style scoped>
/* Footer Base */

.footer {
    background-color: #ffffff;
    border-top: 1px solid #e5e7eb;
    padding: 60px 20px;
    transition: background-color 0.3s ease, border-color 0.3s ease;
}

.container {
    max-width: 100%;
    margin: 0 auto;
}

.footer-top {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 40px;
    margin-bottom: 40px;
}

/* Logo */

.logo {
    font-weight: 800;
}

.text-pink {
    color: var(--primary-pink);
}

/* Navigation */

.nav {
    display: flex;
    flex-wrap: wrap;
    gap: 30px;
}

.nav-link {
    position: relative;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    transition: color 0.3s ease;
}

.nav-link:hover {
    color: #ff4d8d;
}

/* Animated underline */

.nav-link::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: -6px;
    transform: translateX(-50%);
    width: 0%;
    height: 2px;
    background-color: #ff4d8d;
    border-radius: 2px;
    transition: width 0.3s ease;
}

.nav-link:hover::after {
    width: 60%;
}

/* Language Icon */

.language {
    color: #9ca3af;
    cursor: pointer;
    transition: color 0.3s ease;
}

.language:hover {
    color: #ff4d8d;
}

/* Bottom Section */

.footer-bottom {
    text-align: center;
    border-top: 1px solid #f3f4f6;
    padding-top: 30px;
}

.footer-bottom p {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #9ca3af;
    opacity: 0.7;
    transition: opacity 0.3s ease;
}

.footer-bottom p:hover {
    opacity: 1;
}

/* Mobile */

@media (min-width: 768px) {
    .footer-top {
        flex-direction: row;
        justify-content: space-between;
    }
}
</style>