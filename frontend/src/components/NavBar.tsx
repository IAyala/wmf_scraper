import React, { useEffect, useRef, useState } from "react";
import { NavLink } from "react-router-dom";

interface IProps {
  onLogout: () => void;
  userRole: string;
}

interface ILink {
  to: string;
  label: string;
}

const VIEW_LINKS: ILink[] = [
  { to: "/overalls", label: "Overalls" },
  { to: "/overalls_country", label: "By Country" },
  { to: "/results_competitor", label: "By Competitor" },
  { to: "/results_path", label: "Results Path" },
  { to: "/rfs_penalties", label: "RFS Penalties" },
];

// Superadmin-only. Grouped behind one menu so the bar fits on a laptop.
const MANAGE_LINKS: ILink[] = [
  { to: "/add_competition", label: "Add Competition" },
  { to: "/load_competition", label: "Load Competition" },
];

const Navbar: React.FC<IProps> = ({ onLogout, userRole }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const [manageOpen, setManageOpen] = useState(false);
  const manageRef = useRef<HTMLLIElement>(null);

  const close = () => {
    setIsCollapsed(true);
    setManageOpen(false);
  };

  // Click anywhere else and the Manage menu goes away.
  useEffect(() => {
    if (!manageOpen) return;
    const onDocumentClick = (event: MouseEvent) => {
      if (!manageRef.current?.contains(event.target as Node)) setManageOpen(false);
    };
    document.addEventListener("mousedown", onDocumentClick);
    return () => document.removeEventListener("mousedown", onDocumentClick);
  }, [manageOpen]);

  return (
    <nav className="navbar navbar-dark bg-dark navbar-expand-xl sticky-top">
      <div className="container">
        <NavLink to={"/overalls"} className="navbar-brand" onClick={close}>
          WMF Scraper
        </NavLink>

        <button
          className="navbar-toggler"
          type="button"
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-controls="navbarNav"
          aria-expanded={!isCollapsed}
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className={`collapse navbar-collapse ${!isCollapsed ? "show" : ""}`} id="navbarNav">
          <ul className="navbar-nav">
            {VIEW_LINKS.map((link) => (
              <li className="nav-item" key={link.to}>
                {/* NavLink sets .active itself, so the current screen is obvious. */}
                <NavLink to={link.to} className="nav-link" onClick={close}>
                  {link.label}
                </NavLink>
              </li>
            ))}

            {userRole === "superadmin" && (
              <li className="nav-item dropdown" ref={manageRef}>
                <button
                  type="button"
                  className="nav-link dropdown-toggle btn btn-link"
                  aria-expanded={manageOpen}
                  onClick={() => setManageOpen(!manageOpen)}
                >
                  Manage
                </button>
                <ul className={`dropdown-menu ${manageOpen ? "show" : ""}`}>
                  {MANAGE_LINKS.map((link) => (
                    <li key={link.to}>
                      <NavLink to={link.to} className="dropdown-item" onClick={close}>
                        {link.label}
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </li>
            )}
          </ul>

          <div className="navbar-nav ms-auto align-items-xl-center mt-2 mt-xl-0">
            <span className="navbar-text me-xl-3" title={`Signed in as ${userRole}`}>
              <span className="badge bg-secondary text-uppercase">{userRole}</span>
            </span>
            <button
              className="btn btn-outline-light btn-sm"
              onClick={() => {
                onLogout();
                close();
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
