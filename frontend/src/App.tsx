import React, { useCallback, useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import About from "./components/About";
import AddCompetition from "./components/AddCompetition";
import CompetitionByCountry from "./components/CompetitionByCountry";
import CompetitionOveralls from "./components/CompetitionOveralls";
import CompetitorPath from "./components/CompetitorPath";
import LoadCompetition from "./components/LoadCompetition";
import Login from "./components/Login";
import Navbar from "./components/NavBar";
import RFSPenalties from "./components/RFSPenalties";
import TasksResultsCompetitor from "./components/TaskResultsCompetitor";
import { User, fetchCurrentUser, logout, setUnauthenticatedHandler } from "./config/api";

function App() {
  const [user, setUser] = useState<User | null>(null);
  // The session lives in an HttpOnly cookie, so only the server can tell us
  // whether we are logged in. Until it answers, render nothing.
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    fetchCurrentUser()
      .then(setUser)
      .finally(() => setCheckingSession(false));
  }, []);

  useEffect(() => {
    setUnauthenticatedHandler(() => setUser(null));
    return () => setUnauthenticatedHandler(null);
  }, []);

  const handleLogout = useCallback(async () => {
    await logout().catch(() => undefined);
    setUser(null);
  }, []);

  if (checkingSession) {
    return null;
  }

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return (
    <React.Fragment>
      <Navbar onLogout={handleLogout} userRole={user.role} />
      <Routes>
        {user.role === "superadmin" && (
          <>
            <Route path={"/add_competition"} element={<AddCompetition />} />
            <Route path={"/load_competition"} element={<LoadCompetition />} />
          </>
        )}
        <Route path={"/overalls"} element={<CompetitionOveralls />} />
        <Route path={"/about"} element={<About />} />
        <Route path={"/overalls_country"} element={<CompetitionByCountry />} />
        <Route path={"/results_competitor"} element={<TasksResultsCompetitor />} />
        <Route path={"/results_path"} element={<CompetitorPath />} />
        <Route path={"/rfs_penalties"} element={<RFSPenalties />} />
      </Routes>
    </React.Fragment>
  );
}

export default App;
