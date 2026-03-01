<template>
    <div class="page-wrapper">
        <section class="hero-section">
    
            <!-- icon on the back -->
            <span class="material-symbols-outlined decor icon-1 highlight-icon">account_balance</span>
            <span class="material-symbols-outlined decor icon-2 highlight-icon">monetization_on</span>
            <span class="material-symbols-outlined decor icon-3 highlight-icon">public</span>
    
            <div class="hero-content">
                <h1>{{ currentFeature.title }}</h1>
                <h2>{{ currentFeature.subtitle }}</h2>
                <p>{{ currentFeature.description }}</p>
            </div>
    
            <div class="hero-divider"></div>
    
        </section>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const featureMap = {
    Flashcards: {
        title: 'Flashcards',
        subtitle: 'Memorize Smarter, Not Harder',
        description: 'Master key economic concepts quickly with interactive flashcards designed for rapid memory retention.'
    },
    Learning: {
        title: 'Learn',
        subtitle: 'Structured & Deep Understanding',
        description: 'Structured lessons with real-world examples to deepen your understanding step by step.'
    },
    Test: {
        title: 'Practice Exam',
        subtitle: 'Challenge Your Knowledge',
        description: 'Test your knowledge with quizzes and scenario-based challenges to reinforce your learning.'
    }
}

const currentFeature = computed(() => {
    return featureMap[route.name] || {
        title: 'EasyEcon',
        subtitle: 'Welcome',
        description: 'Select a feature to begin learning.'
    }
})
</script>

<style scoped>
.page-wrapper {
    min-height: 38vh;
    background: linear-gradient( 90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
}

/* ---- Hero section (Top) ---- */

/* - hero section - */

.hero-section {
    position: relative;
    text-align: left;
    padding-top: 10px;
}

.hero-section {
    position: relative;
    width: 100%;
    padding: 80px 8%;
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 900px;
}

/* TITLE */

.hero-section h1 {
    color: var(--primary-pink);
    font-size: 80px;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1;
    margin-bottom: 20px;
}

/* SUBTITLE */

.hero-section h2 {
    font-size: 28px;
    font-weight: 700;
    color: var(--text--main);
    margin-bottom: 20px;
}

/* DESCRIPTION */

.hero-section p {
    font-size: 18px;
    line-height: 1.7;
    color: #5c647c;
    max-width: 600px;
}

/* Decorative Icons */

.decor {
    position: absolute;
    z-index: 0;
    opacity: 0.15;
    pointer-events: none;
    filter: blur(1px);
}

.icon-1 {
    top: 10%;
    right: 20%;
    font-size: 150px;
}

.icon-2 {
    bottom: 10%;
    right: 35%;
    font-size: 120px;
}

.icon-3 {
    top: 30;
    right: -30px;
    font-size: 240px;
}

/* ---- divider ---- */

.hero-divider {
    align-items: left;
    width: 98%;
    height: 3px;
    margin: 25px 0 0 0;
    border-radius: 999px;
    background: #ffffff;
}

.highlight-icon {
    background: linear-gradient( 90deg, rgb(255, 185, 65), var(--primary-pink));
    background-size: 150% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s ease-in-out infinite, floatRotate 4s ease-in-out infinite;
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