import React from "react";
import { IconType } from "react-icons";
import { FiCreditCard, FiMail, FiUser, FiUsers } from "react-icons/fi";

interface CardProps {
  title: string;
  subtitle: string;
  Icon: IconType;
  color: string;
}

const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#082032] text-white p-6">
      <h1 className="text-3xl font-bold mb-6">RCs</h1>

      <div className="flex flex-col gap-4">
        <Card
          title="Account"
          subtitle="Manage profile"
          Icon={FiUser}
          color="#217379"
        />
        <Card
          title="Email"
          subtitle="Manage email"
          Icon={FiMail}
          color="#1a3c7d"
        />
        <Card
          title="Team"
          subtitle="Manage team"
          Icon={FiUsers}
          color="#60d4ea"
        />
        <Card
          title="Billing"
          subtitle="Manage cards"
          Icon={FiCreditCard}
          color="#04293A"
        />
      </div>
    </div>
  );
};

const Card: React.FC<CardProps> = ({ title, subtitle, Icon, color }) => {
  const IconComponent = Icon;

  return (
    <a
      href="#"
      className="w-full p-4 rounded-lg shadow-md relative overflow-hidden group bg-[#1a1a40] transition-transform duration-300 hover:scale-105"
    >
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ backgroundColor: color }}
      />

      <IconComponent className="mb-2 text-3xl text-[#60d4ea] group-hover:text-white relative z-10 transition-colors duration-300" />
      <h3 className="font-semibold text-lg group-hover:text-white relative z-10">
        {title}
      </h3>
      <p className="text-slate-300 group-hover:text-slate-200 relative z-10">
        {subtitle}
      </p>
    </a>
  );
};

export default Dashboard;
