import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/auth";

const Login: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await login(username, password);
      navigate("/dashboard"); // redireciona após login
    } catch (err) {
      setError("Usuário ou senha incorretos.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#082032]">
      <form
        onSubmit={handleSubmit}
        className="bg-[#1a1a40] p-8 rounded-2xl shadow-lg w-full max-w-sm"
      >
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Login</h2>

        {error && (
          <div className="bg-red-500 text-white p-2 rounded mb-4 text-center">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="block text-white mb-2">Usuário</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 rounded bg-[#04293A] text-white outline-none"
            required
          />
        </div>

        <div className="mb-6">
          <label className="block text-white mb-2">Senha</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-2 rounded bg-[#04293A] text-white outline-none"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-[#217379] hover:bg-[#60d4ea] text-white font-bold py-2 px-4 rounded transition-colors"
        >
          Entrar
        </button>
      </form>
    </div>
  );
};

export default Login;
