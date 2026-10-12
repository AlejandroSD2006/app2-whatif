<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['submit'])
const question = ref('')
const year = ref('1492')
const unrealismLevel = ref('realista')
const error = ref('')
const questionLength = computed(() => question.value.trim().length)

const levels = [
  { value: 'realista', label: 'Realista', note: 'Plausible' },
  { value: 'ilusionante', label: 'Ilusionante', note: 'Optimista' },
  { value: 'descerebrado', label: 'Descerebrado', note: 'Sin límites' }
]

function submit() {
  const normalizedQuestion = question.value.trim()
  const numericYear = Number(year.value)

  if (!normalizedQuestion) {
    error.value = 'Escribe una hipótesis para empezar.'
  } else if (normalizedQuestion.length > 280) {
    error.value = 'La hipótesis debe tener 280 caracteres o menos.'
  } else if (!Number.isInteger(numericYear) || numericYear < 0 || numericYear > 3000) {
    error.value = 'El año debe ser un número entero entre 0 y 3000.'
  } else {
    error.value = ''
    emit('submit', {
      question: normalizedQuestion,
      year: numericYear,
      unrealismLevel: unrealismLevel.value
    })
  }
}
</script>

<template>
  <form class="hypothesis-form" @submit.prevent="submit">
    <div class="form-heading">
      <span class="section-index">01</span>
      <h2>Plantea el cambio</h2>
    </div>

    <div class="field-block">
      <div class="field-label-row">
        <label for="question">¿Qué habría pasado si...?</label>
        <span class="character-count" :class="{ 'is-over-limit': questionLength > 280 }">
          {{ questionLength }} / 280
        </span>
      </div>
      <textarea
        id="question"
        v-model="question"
        name="question"
        rows="4"
        placeholder="La imprenta se hubiera inventado mil años antes"
        :disabled="props.busy"
        aria-describedby="question-hint"
      />
      <p id="question-hint" class="field-hint">Una hipótesis histórica, en una frase.</p>
    </div>

    <div class="field-block year-block">
      <label for="year">Año de referencia</label>
      <div class="year-input-wrap">
        <input
          id="year"
          v-model="year"
          name="year"
          type="number"
          min="0"
          max="3000"
          step="1"
          inputmode="numeric"
          :disabled="props.busy"
        />
        <span aria-hidden="true">d. C.</span>
      </div>
    </div>

    <fieldset class="field-block level-block" :disabled="props.busy">
      <legend>¿Qué tono debería tener?</legend>
      <div class="level-options">
        <label
          v-for="level in levels"
          :key="level.value"
          class="level-option"
          :class="{ 'is-selected': unrealismLevel === level.value }"
        >
          <input v-model="unrealismLevel" type="radio" name="unrealismLevel" :value="level.value" />
          <span class="level-label">{{ level.label }}</span>
          <span class="level-note">{{ level.note }}</span>
        </label>
      </div>
    </fieldset>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>

    <button class="submit-button" type="submit" :disabled="props.busy">
      <span>{{ props.busy ? 'Imaginando…' : 'Generar escenario' }}</span>
      <span class="submit-arrow" aria-hidden="true">↗</span>
    </button>
  </form>
</template>

<style scoped>
.hypothesis-form {
  display: grid;
  gap: 28px;
}

.form-heading {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.section-index {
  color: #a54e38;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
}

.form-heading h2 {
  margin: 0;
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 28px;
  font-weight: 400;
}

.field-block {
  display: grid;
  gap: 10px;
  min-width: 0;
  margin: 0;
  padding: 0;
  border: 0;
}

.field-label-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

label,
legend {
  color: #244237;
  font-size: 14px;
  font-weight: 700;
}

.character-count,
.field-hint,
.level-note {
  color: #63726b;
  font-size: 12px;
}

.character-count.is-over-limit {
  color: #a83f2c;
}

textarea,
.year-input-wrap {
  width: 100%;
  border: 1px solid #bdc9bd;
  border-radius: 3px;
  background: #fff;
  color: #18372d;
}

textarea {
  min-height: 112px;
  padding: 14px 15px;
  resize: vertical;
  font: inherit;
  line-height: 1.55;
}

textarea::placeholder {
  color: #8b9890;
}

textarea:focus-visible,
input:focus-visible {
  outline: 2px solid #315e49;
  outline-offset: 2px;
}

.field-hint {
  margin: -3px 0 0;
}

.year-block {
  max-width: 220px;
}

.year-input-wrap {
  display: flex;
  align-items: center;
  min-height: 46px;
  padding-right: 12px;
}

.year-input-wrap input {
  width: 100%;
  min-width: 0;
  padding: 10px 12px;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
}

.year-input-wrap span {
  color: #63726b;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  white-space: nowrap;
}

.level-block legend {
  margin-bottom: 10px;
}

.level-options {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border: 1px solid #bdc9bd;
  border-radius: 3px;
  overflow: hidden;
}

.level-option {
  display: grid;
  gap: 5px;
  min-width: 0;
  padding: 12px 10px;
  border-right: 1px solid #bdc9bd;
  background: #fff;
  cursor: pointer;
}

.level-option:last-child {
  border-right: 0;
}

.level-option.is-selected {
  background: #e5eedf;
  box-shadow: inset 0 -3px #315e49;
}

.level-option input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
}

.level-option:has(input:focus-visible) {
  outline: 2px solid #315e49;
  outline-offset: -3px;
}

.level-label {
  font-size: 13px;
  overflow-wrap: anywhere;
}

.level-note {
  font-size: 11px;
}

.form-error {
  margin: -12px 0 0;
  color: #a83f2c;
  font-size: 13px;
}

.submit-button {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 54px;
  padding: 0 18px;
  border: 0;
  border-radius: 3px;
  background: #1d4335;
  color: #fff;
  font: inherit;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.submit-button:hover:not(:disabled) {
  background: #2d6049;
}

.submit-button:focus-visible {
  outline: 3px solid #c8dd63;
  outline-offset: 3px;
}

.submit-button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.submit-arrow {
  font-size: 20px;
  font-weight: 400;
}

@media (max-width: 520px) {
  .hypothesis-form {
    gap: 23px;
  }

  .level-option {
    padding: 11px 7px;
  }

  .level-label {
    font-size: 12px;
  }
}
</style>