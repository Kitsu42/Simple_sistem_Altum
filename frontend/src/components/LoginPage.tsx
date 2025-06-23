// src/components/LoginPage.tsx
import { useNavigate } from "react-router-dom";
import { useAuth } from "../App";

const fakeUser = {
  username: "user01",
  password: "user01",
};

export default function LoginPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const username = (form.username as HTMLInputElement).value;
    const password = (form.password as HTMLInputElement).value;
    if (username === fakeUser.username && password === fakeUser.password) {
      setUser({ username });
      navigate("/rcs");
    } else {
      alert("Usuário ou senha inválidos.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <form
        onSubmit={handleLogin}
        className="bg-gray-800 p-6 rounded shadow-md space-y-4 w-full max-w-sm"
      >
        <h2 className="text-2xl font-bold text-center">Login</h2>
        <input
          name="username"
          placeholder="Usuário"
          className="border p-2 w-full rounded bg-gray-700 text-white"
          required
        />
        <input
          name="password"
          type="password"
          placeholder="Senha"
          className="border p-2 w-full rounded bg-gray-700 text-white"
          required
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white w-full py-2 rounded"
        >
          Entrar
        </button>
      </form>
    </div>
  );
}
