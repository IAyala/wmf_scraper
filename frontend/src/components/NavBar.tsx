import React, { useState } from "react";
import { Link } from "react-router-dom";

interface IProps {
  onLogout: () => void;
  userRole: string;
}

let Navbar: React.FC<IProps> = ({ onLogout, userRole }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);

  const toggleNavbar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <React.Fragment>
      <nav className="navbar navbar-dark bg-dark navbar-expand-sm">
        <div className="container">
          <Link to={"/"} className="navbar-brand">
            WMF Scraper Main Menu
          </Link>

          {/* Hamburger menu button for mobile */}
          <button
            className="navbar-toggler"
            type="button"
            onClick={toggleNavbar}
            aria-controls="navbarNav"
            aria-expanded={!isCollapsed}
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>

          <div className={`collapse navbar-collapse ${!isCollapsed ? 'show' : ''}`} id="navbarNav">
            <ul className="navbar-nav">
              {/* Superadmin-only navigation items */}
              {userRole === 'superadmin' && (
                <>
                  <li className="nav-item">
                    <Link to={"/add_competition"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                      Add Competition
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link to={"/load_competition"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                      Load Competition
                    </Link>
                  </li>
                </>
              )}
              <li className="nav-item">
                <Link to={"/overalls"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                  Competition Overalls
                </Link>
              </li>
              <li className="nav-item">
                <Link to={"/overalls_country"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                  Country Overalls
                </Link>
              </li>
              <li className="nav-item">
                <Link to={"/results_competitor"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                  Results Competitor
                </Link>
              </li>
              <li className="nav-item">
                <Link to={"/results_path"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                  Competitor Results Path
                </Link>
              </li>
              <li className="nav-item">
                <Link to={"/rfs_penalties"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                  RFS Penalties
                </Link>
              </li>
              <li className="nav-item">
                <Link to={"/about"} className="nav-link" onClick={() => setIsCollapsed(true)}>
                  About
                </Link>
              </li>
            </ul>
            <div className="navbar-nav ms-auto">
              <span className="navbar-text me-3">
                Role: <span className="badge bg-secondary">{userRole}</span>
              </span>
              <button
                className="btn btn-outline-light btn-sm"
                onClick={() => {
                  onLogout();
                  setIsCollapsed(true);
                }}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
    </React.Fragment>
  );
};
export default Navbar;
