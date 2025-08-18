// src/services/auth.ts
import axios from "axios";

const API_URL = "http://localhost:8000"; // ajuste se o backend rodar em outra porta

interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const login = async (username: string, password: string) => {
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  return response.json();
};

export const getProfile = async (token: string) => {
  const response = await fetch(`${API_URL}/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Unauthorized");
  }

  return response.json();
};
