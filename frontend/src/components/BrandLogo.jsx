import logo from "../assets/datanova-logo.png";

export default function BrandLogo({
  className = "",
}) {
  return (
    <img
      src={logo}
      alt="DataNova AI"
      className={`datanova-brand-logo ${className}`}
    />
  );
}