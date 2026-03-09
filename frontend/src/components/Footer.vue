<template>
  <footer class="footer">
    <div class="footer-container">

      <!-- Brand -->
      <div class="footer-brand">
        <div class="logo">
          Easy<span class="text-pink">Econ</span>
        </div>

        <p class="footer-desc">
          Developed as part of the course 
          <strong>204212 – Modern Application Development</strong>,
          Department of Computer Science, Chiang Mai University.
        </p>

      </div>

      <!-- Divider -->
      <div class="footer-divider"></div>

      <!-- Bottom -->
      <div class="footer-bottom">
        <p>© {{ currentYear }} Easy Econ</p>
        <span class="footer-tagline">
          Built for future economists
        </span>
      </div>

    </div>
  </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.footer{
  padding:50px 20px 30px;
  background:var(--white);
  border-top:1px solid var(--card-border);
}

/* container */

.footer-container{
  max-width:900px;
  margin:0 auto;
  text-align:center;
}

/* logo */

.logo{
  font-size:30px;
  font-weight:800;
  letter-spacing:-0.5px;
  margin-bottom:14px;
}

/* description */

.footer-desc{
  font-size:14px;
  color:var(--text-muted);
  line-height:1.6;
  max-width:520px;
  margin:0 auto 16px auto;
}

/* badge */

.footer-badge{
  display:inline-block;
  padding:6px 14px;
  font-size:12px;
  font-weight:600;
  border-radius:20px;
  background:var(--light-pink);
  color:var(--primary-pink);
}

/* divider */

.footer-divider{
  height:1px;
  background:var(--card-border);
  margin:45px 0 25px;
}

/* bottom */

.footer-bottom{
  display:flex;
  justify-content:center;
  align-items:center;
  gap:10px;
  flex-wrap:wrap;
  font-size:12px;
  color:var(--text-muted);
}

.footer-tagline{
  opacity:0.7;
}

/* hover subtle */

.footer-tagline:hover{
  opacity:1;
  transition:0.25s;
}

</style>