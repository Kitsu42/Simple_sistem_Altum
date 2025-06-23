// src/App.tsx
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useState, createContext, useContext } from "react";
import RCListPage from "./components/RCListPage";
import LoginPage from "./components/LoginPage";

const AuthContext = createContext<any>(null);
export function useAuth() {
  return useContext(AuthContext);
}

export default function App() {
  const [user, setUser] = useState(null);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/rcs" element={<RCListPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthContext.Provider>
  );
}
