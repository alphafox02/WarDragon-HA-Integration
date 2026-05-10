import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

export default {
  input: "src/wardragon-cop-card.ts",
  output: {
    file: "dist/wardragon-cop-card.js",
    // IIFE so the bundle works when HA loads it via a plain <script> tag
    // (add_extra_js_url is not module-aware). Matches the pattern most
    // HACS-distributed Lovelace cards use.
    format: "iife",
    name: "WarDragonCopCard",
    sourcemap: false,
    inlineDynamicImports: true,
  },
  plugins: [
    resolve({ browser: true }),
    commonjs(),
    typescript({ tsconfig: "./tsconfig.json" }),
    terser({
      format: { comments: false },
      compress: { passes: 2 },
    }),
  ],
};
