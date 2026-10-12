import { createApp } from 'vue'
import { clerkPlugin } from '@clerk/vue'
import App from './App.vue'

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY
const app = createApp(App, { clerkConfigured: Boolean(publishableKey) })

if (publishableKey) {
	app.use(clerkPlugin, { publishableKey })
}

app.mount('#app')