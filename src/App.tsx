// Minimal stlite loader: mounts the Python Streamlit application and CSV dataset in the browser.
import { useEffect, useRef } from "react";

const STLITE = "https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build";

const pySources = import.meta.glob("../streamlit_app/**/*.py", { query: "?raw", import: "default", eager: true }) as Record<string, string>;
const csvSources = import.meta.glob("../streamlit_app/data/*.csv", { query: "?raw", import: "default", eager: true }) as Record<string, string>;
const files = Object.fromEntries(
  Object.entries({ ...pySources, ...csvSources }).map(([p, content]) => [p.replace("../streamlit_app/", ""), content]),
);

export default function App() {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = `${STLITE}/stlite.css`;
    document.head.appendChild(css);
    let controller: { unmount: () => void } | undefined;
    import(/* @vite-ignore */ `${STLITE}/stlite.js`).then(({ mount }) => {
      controller = mount({
        entrypoint: "app.py",
        files,
        requirements: ["plotly", "folium"],
        streamlitConfig: {
          "theme.base": "light",
          "theme.primaryColor": "#0B5FFF",
          "theme.backgroundColor": "#F6F8FB",
          "theme.secondaryBackgroundColor": "#FFFFFF",
          "theme.textColor": "#0F172A",
          "client.toolbarMode": "minimal",
        },
      }, root.current!);
    });
    return () => controller?.unmount();
  }, []);
  return <div ref={root} className="min-h-screen" />;
}
