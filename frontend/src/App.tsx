import React, { useCallback, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import AddCompetition from "./components/AddCompetition";
import CompetitionByCountry from "./components/CompetitionByCountry";
import CompetitionOveralls from "./components/CompetitionOveralls";
import CompetitorPath from "./components/CompetitorPath";
import EditCompetitions from "./components/EditCompetitions";
import LoadCompetition from "./components/LoadCompetition";
import Login from "./components/Login";
import Navbar from "./components/NavBar";
import RFSPenalties from "./components/RFSPenalties";
import StatusBar from "./components/StatusBar";
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
    return (
      <React.Fragment>
        <Login onLogin={setUser} />
        <StatusBar />
      </React.Fragment>
    );
  }

  return (
    <React.Fragment>
      <Navbar onLogout={handleLogout} userRole={user.role} />
      <Routes>
        {user.role === "superadmin" && (
          <>
            <Route path={"/add_competition"} element={<AddCompetition />} />
            <Route path={"/load_competition"} element={<LoadCompetition />} />
            <Route path={"/edit_competitions"} element={<EditCompetitions />} />
          </>
        )}
        <Route path={"/overalls"} element={<CompetitionOveralls />} />
        <Route path={"/overalls_country"} element={<CompetitionByCountry />} />
        <Route path={"/results_competitor"} element={<TasksResultsCompetitor />} />
        <Route path={"/results_path"} element={<CompetitorPath />} />
        <Route path={"/rfs_penalties"} element={<RFSPenalties />} />
        {/* "/" and anything unrecognised land on the standings. */}
        <Route path="*" element={<Navigate to="/overalls" replace />} />
      </Routes>
      <StatusBar />
    </React.Fragment>
  );
}

export default App;
