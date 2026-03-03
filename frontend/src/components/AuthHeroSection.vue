// === Reusable hero section for auth pages === //

<template>
    <div class="hero-section">
        <span class="material-symbols-outlined decor icon-1 highlight-icon">account_balance</span>
        <span class="material-symbols-outlined decor icon-2 highlight-icon">monetization_on</span>
        <span class="material-symbols-outlined decor icon-3 highlight-icon">public</span>
    
        <div class="hero-content">
            <div class="logo-circle">
                <div class="logo-stack">
                    <img src="@/assets/EasyEcon_logo_white.png" alt="EasyEcon Logo" class="main-logo" />
                </div>
            </div>
            <h1>Easy<span class="highlight">Econ</span></h1>
            <h2>Welcome to Econ Learning space</h2>
            <div class="tagline-group">
                <p class="tagline">Everyday Economics, Made Simple.</p>
                <p class="university">Based on Faculty Of Economics — Chiang Mai University</p>
            </div>
        </div>
    </div>
</template>

<script setup>
defineProps({
    subtitle: {
        type: String,
        default: 'Welcome to Econ Learning space'
    }
});
</script>

<style scoped>
.hero-section {
    flex: 1;
    background: radial-gradient(circle at 30% 20%, var(--primary-pink), var(--primary-hover));
    position: relative;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    padding: 40px;
}

/* --- icon ---*/

.decor {
    position: absolute;
    color: white;
    opacity: 0.20;
}

.icon-1 {
    top: 10%;
    left: 10%;
    font-size: 120px;
    transform: rotate(-12deg);
}

.icon-2 {
    bottom: 5%;
    right: 85%;
    font-size: 100px;
    transform: rotate(-10deg);
}

.icon-3 {
    top: 45%;
    right: -50px;
    font-size: 250px;
    opacity: 0.08;
}

/* --- Logo --- */

.logo-circle {
    width: 200px;
    height: 200px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto 30px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.main-logo {
    width: 70%;
    height: auto;
    display: block;
    margin: 0 auto;
}

/* --- Content --- */

.hero-content {
    position: relative;
    z-index: 10;
    text-align: center;
}

.hero-section h1 {
    font-size: 4rem;
    margin: 0;
    font-weight: 900;
}

.hero-section h2 {
    font-size: 1.8rem;
    opacity: 0.9;
    margin-bottom: 20px;
}

.tagline {
    font-size: 1.2rem;
    margin-bottom: 5px;
}

.university {
    font-size: 0.85rem;
    opacity: 0.7;
    font-weight: 300;
}

/* --- Effect --- */

.highlight {
    background: linear-gradient( 90deg, #fde047, #facc15, #f59e0b, #fde047);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 2s ease-in-out infinite;
}

.highlight-icon {
    background: linear-gradient( 90deg, #fffcee, #e9ddab, rgb(255, 185, 65), #fffef8);
    background-size: 150% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s ease-in-out infinite, floatRotate 4s ease-in-out infinite;
}

@keyframes shine {
    0% {
        background-position: 0% center;
    }
    50% {
        background-position: 100% center;
    }
    100% {
        background-position: 0% center;
    }
}

@keyframes floatRotate {
    0% {
        transform: translateY(0px) rotate(0deg);
    }
    50% {
        transform: translateY(-15px) rotate(10deg);
    }
    100% {
        transform: translateY(0px) rotate(0deg);
    }
}
</style>