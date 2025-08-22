import axios from "axios";

const API_URL = "http://localhost:8000/api/v1/auth";

export const login = async (username: string, password: string) => {
  const response = await axios.post(`${API_URL}/login`, {
    username,
    password,
  });
  if (response.data.access_token) {
    localStorage.setItem("token", response.data.access_token);
  }
  return response.data;
};


export const logout = () => {
  localStorage.removeItem("token");
};

export const getToken = () => {
  return localStorage.getItem("token");
};
