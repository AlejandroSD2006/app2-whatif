<script setup>
defineProps({
  result: { type: Object, default: null },
  busy: { type: Boolean, default: false },
  error: { type: String, default: '' }
})
</script>

<template>
  <section class="result-panel" aria-live="polite" aria-busy="busy">
    <div class="result-heading">
      <span class="section-index">02</span>
      <h2>El otro curso de la historia</h2>
    </div>

    <div v-if="busy" class="result-state loading-state">
      <span class="state-mark" aria-hidden="true">…</span>
      <p>Reordenando los acontecimientos</p>
    </div>

    <div v-else-if="error" class="result-state error-state" role="alert">
      <span class="state-mark" aria-hidden="true">!</span>
      <p>{{ error }}</p>
    </div>

    <article v-else-if="result" class="scenario-copy">
      <p class="narrative">{{ result.narrative }}</p>
      <div class="consequences-heading">
        <span>Consecuencias posibles</span>
        <span class="rule" aria-hidden="true" />
      </div>
      <ol class="consequences-list">
        <li v-for="(consequence, index) in result.consequences" :key="`${index}-${consequence}`">
          <span class="consequence-index">0{{ index + 1 }}</span>
          <span>{{ consequence }}</span>
        </li>
      </ol>
    </article>

    <div v-else class="result-state empty-state">
      <span class="empty-stamp" aria-hidden="true">¿Y si?</span>
      <p>Un pequeño cambio puede abrir un mundo distinto.</p>
    </div>
  </section>
</template>

<style scoped>
.result-panel {
  display: flex;
  min-height: 100%;
  flex-direction: column;
  padding: 36px clamp(22px, 4vw, 54px);
  background-color: #eaf0e6;
}

.result-heading {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.section-index {
  color: #a54e38;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
}

.result-heading h2 {
  margin: 0;
  color: #18372d;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 28px;
  font-weight: 400;
}

.result-state {
  display: grid;
  align-content: center;
  justify-items: start;
  flex: 1;
  min-height: 260px;
}

.state-mark {
  color: #ad583b;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 40px;
}

.result-state p {
  max-width: 280px;
  margin: 12px 0 0;
  color: #52675b;
  font-size: 15px;
  line-height: 1.6;
}

.empty-stamp {
  display: grid;
  width: 96px;
  aspect-ratio: 1;
  place-items: center;
  border: 1px solid #91a593;
  border-radius: 50%;
  color: #315e49;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 21px;
  transform: rotate(-9deg);
}

.scenario-copy {
  padding-top: 30px;
}

.narrative {
  margin: 0 0 30px;
  color: #213e33;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 21px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.consequences-heading {
  display: flex;
  align-items: center;
  gap: 14px;
  color: #244237;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.rule {
  height: 1px;
  flex: 1;
  background: #b6c6b6;
}

.consequences-list {
  display: grid;
  gap: 0;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.consequences-list li {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 12px;
  padding: 15px 0;
  border-bottom: 1px solid #c9d4c7;
  color: #314b3e;
  font-size: 14px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.consequence-index {
  color: #a54e38;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  padding-top: 2px;
}

.error-state p {
  color: #8f3529;
}

@media (max-width: 760px) {
  .result-panel {
    min-height: 320px;
    padding: 28px 22px;
  }

  .result-state {
    min-height: 220px;
  }

  .scenario-copy {
    padding-top: 22px;
  }

  .narrative {
    font-size: 19px;
  }
}
</style>