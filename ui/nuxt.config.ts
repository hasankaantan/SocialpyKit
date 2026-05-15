import tailwindcss from "@tailwindcss/vite"

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-12-01",
  devtools: { enabled: true },

  modules: [
    "@pinia/nuxt",
    "@vueuse/nuxt",
    "@nuxtjs/sitemap",
    "@nuxtjs/robots",
  ],

  css: ["~/assets/css/main.css"],

  // Disable component auto-import. The codebase uses explicit imports
  // throughout (matching shadcn-vue's documented pattern). Auto-import on
  // top of explicit imports triggers Nuxt's duplicate-component warning
  // for each shadcn `index.ts` ↔ `Component.vue` pair.
  components: {
    dirs: [],
  },

  vite: {
    plugins: [tailwindcss()],
  },

  runtimeConfig: {
    public: {
      apiBase: "http://localhost:8000",
      siteUrl: "http://localhost:3000",
    },
  },

  // Hybrid render rules — public pages prerendered at build time,
  // auth pages SSR, dashboard SPA-only (no server hydration).
  routeRules: {
    "/": { prerender: true },
    "/pricing": { prerender: true },
    "/sitemap.xml": { prerender: true },
    "/robots.txt": { prerender: true },
    "/login": { ssr: true },
    "/register": { ssr: true },
    "/dashboard/**": { ssr: false },
  },

  site: {
    url: "http://localhost:3000",
    name: "SocialpyKit",
  },

  // Sitemap covers public marketing routes only; auth + dashboard are
  // excluded since they should not be indexed.
  sitemap: {
    exclude: ["/login", "/register", "/dashboard/**"],
  },

  // Same exclusion list for crawlers via robots.txt.
  robots: {
    disallow: ["/login", "/register", "/dashboard/"],
  },

  typescript: {
    strict: true,
    typeCheck: false,
  },

  app: {
    head: {
      htmlAttrs: { lang: "en" },
      link: [{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
    },
  },
})
