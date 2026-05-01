import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav>
      <div className="nav-logo" onClick={() => navigate('/')}>
        <div className="logo-mark">NE</div>
        <div className="logo-text">Neural<span>Eye</span></div>
      </div>
      <div className="nav-links">
        <NavLink to="/" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>Home</NavLink>
        <NavLink to="/image" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>Image</NavLink>
        <NavLink to="/video" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>Video</NavLink>
        <NavLink to="/model-info" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>Model Info</NavLink>
        <NavLink to="/community" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>Community</NavLink>
      </div>
    </nav>
  );
}
