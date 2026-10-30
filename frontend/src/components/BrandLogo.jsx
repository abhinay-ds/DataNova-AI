import React from "react";

export default function BrandLogo({
  variant = "full", // "full" | "icon"
  size = "md",      // "sm" | "md" | "lg"
  className = "",
  style = {},
}) {
  // Dimensions map
  const dimensions = {
    sm: { icon: 26, text: 15, badge: 10, gap: 8, height: 28 },
    md: { icon: 32, text: 18, badge: 11, gap: 10, height: 34 },
    lg: { icon: 40, text: 22, badge: 12, gap: 12, height: 42 },
  };

  const dim = dimensions[size] || dimensions.md;

  return (
    <div
      className={`datanova-brand-logo-wrap ${className}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: `${dim.gap}px`,
        textDecoration: "none",
        userSelect: "none",
        lineHeight: 1,
        ...style,
      }}
      aria-label="DataNova AI"
    >
      {/* CRISP SVG BRAND ICON */}
      <svg
        width={dim.icon}
        height={dim.icon}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ flexShrink: 0, display: "block" }}
      >
        <defs>
          <linearGradient id="dnGradBg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#2563eb" />
            <stop offset="50%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#7c3aed" />
          </linearGradient>
          <linearGradient id="dnGradBeam" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
            <stop offset="50%" stopColor="#e0f2fe" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#c084fc" stopOpacity="0.9" />
          </linearGradient>
          <filter id="dnGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Squircle container with brand gradient */}
        <rect
          x="1"
          y="1"
          width="46"
          height="46"
          rx="12"
          fill="url(#dnGradBg)"
        />

        {/* Subtle inner border for crispness */}
        <rect
          x="1"
          y="1"
          width="46"
          height="46"
          rx="12"
          stroke="#ffffff"
          strokeWidth="1"
          strokeOpacity="0.25"
          fill="none"
        />

        {/* Stylized Modern "N" + Nova Star geometry */}
        {/* Left vertical data pillar */}
        <path
          d="M14 34V14C14 12.8954 14.8954 12 16 12C17.1046 12 18 12.8954 18 14V34C18 35.1046 17.1046 36 16 36C14.8954 36 14 35.1046 14 34Z"
          fill="#ffffff"
          fillOpacity="0.92"
        />

        {/* Right vertical data pillar */}
        <path
          d="M30 34V14C30 12.8954 30.8954 12 32 12C33.1046 12 34 12.8954 34 14V34C34 35.1046 33.1046 36 32 36C30.8954 36 30 35.1046 30 34Z"
          fill="#ffffff"
          fillOpacity="0.92"
        />

        {/* Dynamic diagonal connection ribbon */}
        <path
          d="M15.5 13.5L32.5 34.5"
          stroke="url(#dnGradBeam)"
          strokeWidth="4"
          strokeLinecap="round"
        />

        {/* Central Nova Spark / Data Node */}
        <g filter="url(#dnGlow)">
          <circle cx="24" cy="24" r="4.5" fill="#ffffff" />
          <path
            d="M24 16.5L25.2 22.8L31.5 24L25.2 25.2L24 31.5L22.8 25.2L16.5 24L22.8 22.8L24 16.5Z"
            fill="#ffffff"
          />
        </g>

        {/* Micro data orbits */}
        <circle cx="16" cy="14" r="2.2" fill="#38bdf8" />
        <circle cx="32" cy="34" r="2.2" fill="#c084fc" />
      </svg>

      {/* WORDMARK (Only when variant is full) */}
      {variant !== "icon" && (
        <span
          className="datanova-wordmark"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "5px",
            fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif",
            fontWeight: 700,
            fontSize: `${dim.text}px`,
            letterSpacing: "-0.03em",
          }}
        >
          <span
            style={{
              color: "var(--dn-text, #0f172a)",
              transition: "color 0.2s ease",
            }}
          >
            Data<span style={{ color: "#2563eb" }}>Nova</span>
          </span>

          <span
            style={{
              background: "linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)",
              color: "#ffffff",
              fontSize: `${dim.badge}px`,
              fontWeight: 800,
              padding: "2px 5px",
              borderRadius: "5px",
              letterSpacing: "0.04em",
              display: "inline-block",
              lineHeight: 1.1,
              boxShadow: "0 2px 6px rgba(37, 99, 235, 0.25)",
            }}
          >
            AI
          </span>
        </span>
      )}
    </div>
  );
}