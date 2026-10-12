<script setup>
import { ref } from 'vue'
import { SignIn, useClerk } from '@clerk/vue'

const props = defineProps({
  configured: { type: Boolean, default: false },
  loaded: { type: Boolean, default: false },
  signedIn: { type: Boolean, default: false },
  location: { type: String, default: 'inline' }
})

const emit = defineEmits(['signed-out'])
const clerk = props.configured ? useClerk() : null
const signingOut = ref(false)

async function signOut() {
  if (!clerk?.value || signingOut.value) return

  signingOut.value = true
  try {
    await clerk.value.signOut()
    emit('signed-out')
  } finally {
    signingOut.value = false
  }
}
</script>

<template>
  <div v-if="props.location === 'toolbar' && props.signedIn" class="toolbar-access">
    <button class="sign-out-button" type="button" :disabled="signingOut" @click="signOut">
      {{ signingOut ? 'Cerrando sesión…' : 'Cerrar sesión' }}
    </button>
  </div>

  <section v-else-if="!props.signedIn" class="access-panel" aria-labelledby="access-title">
    <template v-if="!props.configured">
      <p class="access-eyebrow">ACCESO SEGURO</p>
      <h2 id="access-title">Tu sesión abre<br /><em>otra historia.</em></h2>
      <p class="access-copy">Para crear un escenario, inicia sesión con Clerk.</p>
      <p class="configuration-message" role="status">
        Configura VITE_CLERK_PUBLISHABLE_KEY para habilitar el acceso.
      </p>
    </template>

    <template v-else-if="!props.loaded">
      <p class="access-eyebrow">ACCESO SEGURO</p>
      <h2 id="access-title">Comprobando<br /><em>tu sesión.</em></h2>
    </template>

    <template v-else>
      <p class="access-eyebrow">ACCESO SEGURO</p>
      <h2 id="access-title">Tu sesión abre<br /><em>otra historia.</em></h2>
      <p class="access-copy">Para crear un escenario, inicia sesión con Clerk.</p>
      <div class="clerk-sign-in">
        <SignIn routing="hash" />
      </div>
    </template>
  </section>
</template>

<style scoped>
.access-panel {
  width: 100%;
  max-width: 410px;
  padding: 8px 0;
}

.access-eyebrow {
  margin: 0 0 12px;
  color: #a54e38;
  font-family: 'DM Mono', monospace;
  font-size: 10px;
}

.access-panel h2 {
  margin: 0;
  color: #17382d;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 34px;
  font-weight: 400;
  line-height: 1.05;
}

.access-panel h2 em {
  color: #a54e38;
  font-weight: 400;
}

.access-copy {
  margin: 13px 0 22px;
  color: #586a5e;
  font-size: 14px;
  line-height: 1.5;
}

.clerk-sign-in {
  width: 100%;
  overflow: hidden;
}

.configuration-message {
  padding: 12px 14px;
  border-left: 3px solid #a54e38;
  background: #f1e9df;
  color: #713e2d;
  font-size: 12px;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.sign-out-button {
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid #bdc9bd;
  border-radius: 3px;
  background: transparent;
  color: #315e49;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.sign-out-button:hover:not(:disabled) {
  background: #e5eedf;
}

.sign-out-button:focus-visible {
  outline: 2px solid #315e49;
  outline-offset: 2px;
}

.sign-out-button:disabled {
  opacity: 0.65;
}

@media (max-width: 520px) {
  .access-panel h2 {
    font-size: 30px;
  }
}
</style>