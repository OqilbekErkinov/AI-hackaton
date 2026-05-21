// nuxt.config.ts
export default defineNuxtConfig({
  app: {
    head: {
      title: "RankEdu - O`zbekiston milliy ta`lim platformasi",
      htmlAttrs: { lang: "uz" },
      link: [
        { rel: "icon", type: "image/png", href: "/favicon.png" },
        {
          rel: "preconnect",
          href: "https://fonts.gstatic.com",
          crossorigin: "",
        },
      ],
    },
    pageTransition: { name: "page", mode: "out-in" },
    layoutTransition: { name: "layout", mode: "out-in" },
  },

  css: [
    "bootstrap/dist/css/bootstrap.min.css",
    "bootstrap-icons/font/bootstrap-icons.css",
    "@/assets/css/main.css",
  ],

  plugins: [
    { src: "~/plugins/bootstrap.client.ts", mode: "client" },
  ],

  runtimeConfig: {
    public: {
      siteName: "RankEdu",
      apiUrl: process.env.NUXT_PUBLIC_API_URL || "http://127.0.0.1:9000/api",
    },
  },

  modules: ["@nuxt/image"],
  image: {
    format: ["avif", "webp"],
    quality: 60,
    screens: { sm: 640, md: 768, lg: 1024, xl: 1280 },
  },
  routeRules: {
    "/_ipx/**": {
      headers: { "cache-control": "public, max-age=31536000, immutable" },
    },
  },

  compatibilityDate: "2025-08-15",
});
