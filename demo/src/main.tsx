// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
// Self-hosted OFL fonts, bundled by Vite and served from this origin. Libre Caslon Text: latin subset, weights used only.
// Karla: variable weight axis; the browser fetches only the subset its unicode-range needs (latin for this page).
import "@fontsource/libre-caslon-text/latin-400.css";
import "@fontsource/libre-caslon-text/latin-700.css";
import "@fontsource-variable/karla/wght.css";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
