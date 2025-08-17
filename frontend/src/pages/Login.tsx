import React, { useState } from "react";

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Login:", { email, password });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#082032] to-[#1a1a40]">
      <div className="bg-[#1a1a40] w-full max-w-md rounded-2xl shadow-2xl p-8">
        <h2 className="text-3xl font-bold text-center text-white mb-2">
          LOGIN
        </h2>
        <p className="text-gray-400 text-center mb-8">
          Please enter your login and password!
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Email */}
          <div>
            <label className="block text-sm text-gray-300 mb-1">Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-[#082032] text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-[#60d4ea]"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm text-gray-300 mb-1">Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-[#082032] text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-[#217379]"
            />
          </div>

          {/* Forgot password */}
          <p className="text-right text-sm text-gray-400 hover:text-[#60d4ea] cursor-pointer">
            Forgot password?
          </p>

          {/* Button */}
          <button
            type="submit"
            className="w-full py-3 mt-2 rounded-lg font-semibold text-white bg-gradient-to-r from-[#217379] to-[#1a3c7d] hover:opacity-90 transition"
          >
            LOGIN
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
