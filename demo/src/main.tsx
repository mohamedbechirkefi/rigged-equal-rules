// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
// Self-hosted OFL fonts (latin subset, weights used only); bundled by Vite, served from this origin.
import "@fontsource/libre-caslon-text/latin-400.css";
import "@fontsource/libre-caslon-text/latin-700.css";
import "@fontsource/barlow-semi-condensed/latin-500.css";
import "@fontsource/barlow-semi-condensed/latin-600.css";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
