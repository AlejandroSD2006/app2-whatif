<script setup>
import { computed, ref } from 'vue'
import { useAuth } from '@clerk/vue'
import ClerkAccess from './components/ClerkAccess.vue'
import HypothesisForm from './components/HypothesisForm.vue'
import ScenarioResult from './components/ScenarioResult.vue'
import { processScenario } from './services/api.js'

const props = defineProps({
  clerkConfigured: { type: Boolean, default: false }
})

const auth = props.clerkConfigured ? useAuth() : null
const isLoaded = computed(() => auth?.isLoaded.value ?? true)
const isSignedIn = computed(() => auth?.isSignedIn.value ?? false)
const result = ref(null)
const busy = ref(false)
const error = ref('')

async function generateScenario(request) {
  if (busy.value) return
  result.value = null
  error.value = ''

  if (!auth || !isSignedIn.value) {
    error.value = 'Inicia sesión para generar un escenario.'
    return
  }

  busy.value = true
  try {
    const token = await auth.getToken.value()
    if (!token) {
      error.value = 'Tu sesión ha caducado. Vuelve a iniciar sesión.'
      return
    }
    result.value = await processScenario(request, token)
  } catch (cause) {
    error.value = cause instanceof Error
      ? cause.message
      : 'No se pudo generar el escenario. Inténtalo de nuevo.'
  } finally {
    busy.value = false
  }
}

function handleSignOut() {
  result.value = null
  error.value = ''
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="#top" aria-label="What If, inicio">
        <span class="brand-mark" aria-hidden="true">W</span>
        <span class="brand-name">WHAT IF<span> / ARCHIVO DE POSIBILIDADES</span></span>
      </a>
      <div class="topbar-actions">
        <span class="edition">HISTORIA ALTERNATIVA <span>·</span> N.º 001</span>
        <ClerkAccess
          v-if="isSignedIn"
          :configured="props.clerkConfigured"
          :loaded="isLoaded"
          :signed-in="isSignedIn"
          location="toolbar"
          @signed-out="handleSignOut"
        />
      </div>
    </header>

    <main id="top">
      <section class="intro" aria-labelledby="page-title">
        <p class="eyebrow">HISTORIA, CON OTRO GIRO</p>
        <h1 id="page-title">El pasado pudo<br /><em>ser distinto.</em></h1>
        <p class="intro-copy">
          Cambia una sola pieza. Explora el mundo que habría aparecido en su lugar.
        </p>
      </section>

      <section class="workbench" aria-label="Generador de historia alternativa">
        <div v-if="!isSignedIn" class="form-column access-column">
          <ClerkAccess
            :configured="props.clerkConfigured"
            :loaded="isLoaded"
            :signed-in="isSignedIn"
            location="inline"
          />
        </div>
        <div v-else class="form-column">
          <HypothesisForm :busy="busy" @submit="generateScenario" />
          <p class="privacy-note"><span aria-hidden="true">●</span> La hipótesis solo vive durante esta sesión.</p>
        </div>
        <ScenarioResult :result="result" :busy="busy" :error="error" />
      </section>
    </main>

    <footer class="page-footer">
      <span>ESCENARIOS HIPOTÉTICOS, NO PREDICCIONES</span>
      <span>01 <span class="footer-rule" aria-hidden="true" /> 01</span>
    </footer>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

:root {
  font-family: 'DM Sans', sans-serif;
  color: #18372d;
  background: #f5f7f2;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-optical-sizing: auto;
  font-weight: 400;
}

* {
  box-sizing: border-box;
}

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
}

button,
input,
textarea {
  font: inherit;
}

button,
a,
input,
textarea {
  -webkit-tap-highlight-color: transparent;
}

.app-shell {
  width: min(100% - 56px, 1240px);
  min-height: 100vh;
  margin: 0 auto;
}

.topbar {
  display: flex;
  min-height: 76px;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #d6dfd4;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  color: inherit;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 31px;
  aspect-ratio: 1;
  place-items: center;
  background: #d8e878;
  color: #1d4335;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 20px;
}

.brand-name,
.edition,
.eyebrow,
.page-footer {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0;
}

.brand-name {
  font-size: 12px;
  font-weight: 500;
}

.brand-name span {
  color: #65756a;
  font-weight: 400;
}

.edition {
  color: #65756a;
  text-align: right;
}

.edition span {
  color: #b25539;
}

.intro {
  max-width: 670px;
  padding: 47px 0 37px;
}

.eyebrow {
  margin: 0 0 13px;
  color: #a54e38;
}

h1 {
  margin: 0;
  color: #17382d;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 52px;
  font-weight: 400;
  line-height: 0.98;
}

h1 em {
  color: #a54e38;
  font-weight: 400;
}

.intro-copy {
  max-width: 440px;
  margin: 16px 0 0;
  color: #586a5e;
  font-size: 15px;
  line-height: 1.55;
}

.workbench {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  align-items: stretch;
  border-top: 1px solid #d6dfd4;
  border-bottom: 1px solid #d6dfd4;
}

.form-column {
  padding: 36px clamp(22px, 4vw, 54px) 28px 0;
}

.access-column {
  display: flex;
  align-items: center;
  min-height: 440px;
}

.privacy-note {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 20px 0 0;
  color: #65756a;
  font-size: 11px;
}

.privacy-note span {
  color: #819948;
  font-size: 8px;
}

.page-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 0 28px;
  color: #718075;
  font-size: 9px;
}

.page-footer > span:last-child {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #a54e38;
}

.footer-rule {
  display: inline-block;
  width: 24px;
  height: 1px;
  background: #a54e38;
}

@media (max-width: 760px) {
  .app-shell {
    width: min(100% - 32px, 560px);
  }

  .topbar {
    min-height: 64px;
  }

  .brand-name span {
    display: none;
  }

  .edition {
    max-width: 135px;
    font-size: 9px;
  }

  .topbar-actions {
    gap: 8px;
  }

  .intro {
    padding: 36px 0 28px;
  }

  h1 {
    font-size: 40px;
  }

  .workbench {
    grid-template-columns: minmax(0, 1fr);
  }

  .form-column {
    padding: 28px 0 24px;
  }

  .access-column {
    min-height: 380px;
  }
}

@media (max-width: 390px) {
  .edition {
    max-width: 110px;
  }

  h1 {
    font-size: 36px;
  }

  .page-footer {
    font-size: 8px;
  }
}
</style>