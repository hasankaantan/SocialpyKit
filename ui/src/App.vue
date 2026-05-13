<script setup lang="ts">
import { onMounted, ref } from "vue"

import LoginForm from "./components/LoginForm.vue"
import RegisterForm from "./components/RegisterForm.vue"
import { useAuthStore } from "./stores/auth"

const store = useAuthStore()
const mode = ref<"login" | "register">("login")

// If a token is hydrated from localStorage at boot we still need to ask
// the backend who that token belongs to. Run once on mount.
onMounted(async () => {
  if (store.isAuthenticated && store.user === null) {
    try {
      await store.fetchMe()
    } catch {
      // Token is stale (expired or revoked) — clear it so the next render
      // shows the login form.
      store.logout()
    }
  }
})
</script>

<template>
  <main class="app">
    <header class="app__header">
      <h1>SocialpyKit</h1>
      <p>FastAPI starter kit — strict types, immutable schemas, async SQLAlchemy.</p>
    </header>

    <section v-if="!store.isAuthenticated" class="app__auth">
      <nav class="tabs">
        <button
          type="button"
          :class="{ tabs__tab: true, 'tabs__tab--active': mode === 'login' }"
          @click="mode = 'login'"
        >
          Sign in
        </button>
        <button
          type="button"
          :class="{ tabs__tab: true, 'tabs__tab--active': mode === 'register' }"
          @click="mode = 'register'"
        >
          Create account
        </button>
      </nav>

      <LoginForm v-if="mode === 'login'" />
      <RegisterForm v-else />
    </section>

    <section v-else class="app__profile">
      <h2>Welcome, {{ store.user?.email }}</h2>
      <dl>
        <dt>User id</dt>
        <dd>{{ store.user?.id }}</dd>
        <dt>Active</dt>
        <dd>{{ store.user?.is_active ? "yes" : "no" }}</dd>
        <dt>Created</dt>
        <dd>{{ store.user?.created_at }}</dd>
      </dl>
      <button type="button" class="app__signout" @click="store.logout">Sign out</button>
    </section>
  </main>
</template>

<style scoped>
.app {
  max-width: 480px;
  margin: 2rem auto;
  padding: 1.5rem;
  font-family:
    system-ui,
    -apple-system,
    "Segoe UI",
    sans-serif;
}

.app__header h1 {
  margin: 0 0 0.25rem;
}

.app__header p {
  margin: 0 0 1.5rem;
  color: #666;
  font-size: 0.875rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #ddd;
}

.tabs__tab {
  padding: 0.5rem 0.75rem;
  border: 0;
  background: transparent;
  cursor: pointer;
  font-size: 0.875rem;
  color: #555;
  border-bottom: 2px solid transparent;
}

.tabs__tab--active {
  color: #1f6feb;
  border-bottom-color: #1f6feb;
  font-weight: 600;
}

.app__profile dl {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.25rem 1rem;
  font-size: 0.875rem;
  margin: 1rem 0;
}

.app__profile dt {
  color: #666;
}

.app__profile dd {
  margin: 0;
  font-family: ui-monospace, "SF Mono", monospace;
}

.app__signout {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}
</style>
