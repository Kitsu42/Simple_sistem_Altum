import React from "react";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div>
      <header>
        <h1>Simple Sistem Altum</h1>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
