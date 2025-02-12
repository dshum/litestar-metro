import {defineConfig} from "vite"
import litestar from "litestar-vite-plugin"
import tailwindcss from "@tailwindcss/vite"
import {viteStaticCopy} from "vite-plugin-static-copy"

const ASSET_URL = process.env.ASSET_URL || "/static/"
const VITE_PORT = process.env.VITE_PORT || "5173"
const VITE_HOST = process.env.VITE_HOST || "localhost"

export default defineConfig({
  base: `${ASSET_URL}`,
  server: {
    host: "0.0.0.0",
    port: +`${VITE_PORT}`,
    cors: true,
    hmr: {
      host: `${VITE_HOST}`,
    },
  },
  plugins: [
    litestar({
      input: [
        "resources/styles.css",
        "resources/main.ts",
      ],
      assetUrl: `${ASSET_URL}`,
      bundleDirectory: "public",
      resourceDirectory: "resources",
      hotFile: "public/hot"
    }),
    tailwindcss(),
    viteStaticCopy({
      targets: [
        {
          src: "resources/images",
          dest: ""
        },
        {
          src: "resources/js",
          dest: ""
        }
      ]
    }),
  ],
  resolve: {
    alias: {
      "@": "resources"
    },
  },
  build: {
    emptyOutDir: true,
  },
})