import { Link, useLocation } from "react-router-dom";

const navStyle = {
  position: "sticky",
  top: 0,
  zIndex: 100,
  background: "linear-gradient(135deg, #0a0f1e 0%, #0d1b35 100%)",
  borderBottom: "1px solid rgba(0, 212, 255, 0.15)",
  backdropFilter: "blur(12px)",
  fontFamily: "'Syne', sans-serif",
};

const innerStyle = {
  maxWidth: "1200px",
  margin: "0 auto",
  padding: "0 2rem",
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  height: "68px",
};

const logoStyle = {
  display: "flex",
  alignItems: "center",
  gap: "10px",
  textDecoration: "none",
};

const logoIconStyle = {
  width: "36px",
  height: "36px",
  background: "linear-gradient(135deg, #00d4ff, #0066ff)",
  borderRadius: "8px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: "18px",
};

const logoTextStyle = {
  color: "#ffffff",
  fontSize: "1.1rem",
  fontWeight: 700,
  letterSpacing: "0.02em",
};

const logoSubStyle = {
  color: "#00d4ff",
  fontSize: "0.65rem",
  letterSpacing: "0.15em",
  textTransform: "uppercase",
};

const linksStyle = {
  display: "flex",
  alignItems: "center",
  gap: "0.25rem",
  listStyle: "none",
  margin: 0,
  padding: 0,
};

function NavLink({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <li>
      <Link
        to={to}
        style={{
          padding: "0.45rem 1rem",
          borderRadius: "6px",
          textDecoration: "none",
          fontFamily: "'Syne', sans-serif",
          fontSize: "0.9rem",
          fontWeight: 500,
          letterSpacing: "0.04em",
          color: isActive ? "#00d4ff" : "rgba(255,255,255,0.75)",
          background: isActive ? "rgba(0,212,255,0.08)" : "transparent",
          border: isActive ? "1px solid rgba(0,212,255,0.25)" : "1px solid transparent",
          transition: "all 0.2s ease",
        }}
        onMouseEnter={e => {
          if (!isActive) {
            e.target.style.color = "#ffffff";
            e.target.style.background = "rgba(255,255,255,0.05)";
          }
        }}
        onMouseLeave={e => {
          if (!isActive) {
            e.target.style.color = "rgba(255,255,255,0.75)";
            e.target.style.background = "transparent";
          }
        }}
      >
        {children}
      </Link>
    </li>
  );
}

export default function Navbar() {
  return (
    <>
      <link
        href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap"
        rel="stylesheet"
      />
      <nav style={navStyle}>
        <div style={innerStyle}>
          <Link to="/" style={logoStyle}>
            <div style={logoIconStyle}>🛡️</div>
            <div>
              <div style={logoTextStyle}>FraudGuard</div>
              <div style={logoSubStyle}>KNN Detection</div>
            </div>
          </Link>

          <ul style={linksStyle}>
            <NavLink to="/">Home</NavLink>
            <NavLink to="/about">About</NavLink>
            <NavLink to="/contact">Contact</NavLink>
            <li>
              <Link
                to="/login"
                style={{
                  marginLeft: "0.5rem",
                  padding: "0.45rem 1.25rem",
                  borderRadius: "6px",
                  textDecoration: "none",
                  fontFamily: "'Syne', sans-serif",
                  fontSize: "0.9rem",
                  fontWeight: 600,
                  letterSpacing: "0.04em",
                  color: "#0a0f1e",
                  background: "linear-gradient(135deg, #00d4ff, #0066ff)",
                  border: "none",
                  transition: "opacity 0.2s ease, transform 0.2s ease",
                  display: "inline-block",
                }}
                onMouseEnter={e => {
                  e.target.style.opacity = "0.88";
                  e.target.style.transform = "translateY(-1px)";
                }}
                onMouseLeave={e => {
                  e.target.style.opacity = "1";
                  e.target.style.transform = "translateY(0)";
                }}
              >
                Login
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </>
  );
}