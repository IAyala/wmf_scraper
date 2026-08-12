import React from "react";
import { useVersion } from "../hooks/useVersion";

/** Fixed bar along the bottom of the window, showing the running version. */
const StatusBar: React.FC = () => {
  const version = useVersion();

  return (
    <footer className="status-bar bg-dark text-light">
      <span>WMF Scraper</span>
      <span title="Version reported by the server">v{version ?? "…"}</span>
    </footer>
  );
};

export default StatusBar;
