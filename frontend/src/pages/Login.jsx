import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Compass,
  Eye,
  EyeOff,
  Loader2,
  LockKeyhole,
  Mail,
  Sparkles,
  UserRound,
} from "lucide-react";

import BrandLogo from "../components/BrandLogo";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    login,
    signup,
    demoLogin,
    guestLogin,
    isAuthenticated,
  } = useAuth();

  const [mode, setMode] = useState("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(null); // "demo" | "guest" | null
  const [error, setError] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const requestedMode = params.get("mode");

    if (requestedMode === "signup") {
      setMode("signup");
    }

    if (params.get("expired") === "1" || params.get("expired") === "true") {
      setError("Your session has expired. Please sign in again to continue.");
    }
  }, [location.search]);

  function switchMode(nextMode) {
    setMode(nextMode);
    setError("");
    setPassword("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password) {
      setError("Please enter your email and password.");
      return;
    }

    if (mode === "signup" && !fullName.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (mode === "signup" && password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    try {
      setLoading(true);

      if (mode === "signup") {
        await signup(
          email.trim(),
          password,
          fullName.trim()
        );
      } else {
        await login(
          email.trim(),
          password
        );
      }

      navigate("/dashboard", {
        replace: true,
      });
    } catch (err) {
      setError(
        err?.message ||
          "Authentication failed. Please check your credentials and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleDemoLogin() {
    setError("");
    setActionLoading("demo");
    try {
      await demoLogin();
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err?.message || "Failed to initialize demo account. Please try again.");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleGuestLogin() {
    setError("");
    setActionLoading("guest");
    try {
      await guestLogin();
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err?.message || "Failed to launch guest session. Please try again.");
    } finally {
      setActionLoading(null);
    }
  }

  const isBusy = loading || actionLoading !== null;

  return (
    <div className="auth-page">
      <div className="auth-shell">

        {/* LOGO & BRANDING */}
        <div className="auth-brand">
          <Link to="/" aria-label="DataNova AI Home">
            <BrandLogo className="login-logo" />
          </Link>
        </div>

        <div className="auth-card">

          {/* HEADLINE */}
          <div className="auth-heading">
            <span className="auth-eyebrow">
              {mode === "login" ? "Welcome back" : "Get started"}
            </span>

            <h1>Your data. Smarter decisions.</h1>

            <p>
              {mode === "login"
                ? "Sign in to access your projects, datasets, and AI workspace."
                : "Create an account to start analyzing your datasets with AI."}
            </p>
          </div>

          {/* TABS */}
          <div className="auth-tabs" role="tablist" aria-label="Authentication modes">
            <button
              type="button"
              role="tab"
              aria-selected={mode === "login"}
              className={
                mode === "login"
                  ? "auth-tab active"
                  : "auth-tab"
              }
              onClick={() => switchMode("login")}
              disabled={isBusy}
            >
              Sign In
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={mode === "signup"}
              className={
                mode === "signup"
                  ? "auth-tab active"
                  : "auth-tab"
              }
              onClick={() => switchMode("signup")}
              disabled={isBusy}
            >
              Create Account
            </button>
          </div>

          {/* ERROR ALERT */}
          {error && (
            <div className="auth-error" role="alert" aria-live="polite">
              {error}
            </div>
          )}

          {/* CREDENTIALS FORM */}
          <form
            className="auth-form"
            onSubmit={handleSubmit}
            noValidate
          >
            {mode === "signup" && (
              <label className="auth-field">
                <span>Full name</span>
                <div className="auth-input-wrap">
                  <UserRound size={18} aria-hidden="true" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(event) =>
                      setFullName(event.target.value)
                    }
                    placeholder="Your name"
                    autoComplete="name"
                    disabled={isBusy}
                    required
                  />
                </div>
              </label>
            )}

            <label className="auth-field">
              <span>Email address</span>
              <div className="auth-input-wrap">
                <Mail size={18} aria-hidden="true" />
                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  placeholder="you@example.com"
                  autoComplete="email"
                  disabled={isBusy}
                  required
                />
              </div>
            </label>

            <label className="auth-field">
              <span>Password</span>
              <div className="auth-input-wrap">
                <LockKeyhole size={18} aria-hidden="true" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  placeholder={mode === "signup" ? "At least 8 characters" : "Enter your password"}
                  autoComplete={
                    mode === "login"
                      ? "current-password"
                      : "new-password"
                  }
                  disabled={isBusy}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                  disabled={isBusy}
                >
                  {showPassword ? (
                    <EyeOff size={17} aria-hidden="true" />
                  ) : (
                    <Eye size={17} aria-hidden="true" />
                  )}
                </button>
              </div>
            </label>

            <button
              type="submit"
              className="auth-submit"
              disabled={isBusy}
              aria-busy={loading}
            >
              {loading ? (
                <>
                  <Loader2
                    size={18}
                    className="auth-spinner"
                    aria-hidden="true"
                  />
                  <span>
                    {mode === "login"
                      ? "Signing in..."
                      : "Creating account..."}
                  </span>
                </>
              ) : (
                <>
                  <span>
                    {mode === "login"
                      ? "Sign in"
                      : "Create account"}
                  </span>
                  <ArrowRight size={18} aria-hidden="true" />
                </>
              )}
            </button>
          </form>

          {/* DIVIDER */}
          <div className="auth-divider" role="separator" aria-label="Alternative entry options">
            <span>or explore instantly</span>
          </div>

          {/* INSTANT ACCESS OPTIONS: DEMO & GUEST */}
          <div className="auth-alt-actions">
            {/* TRY DEMO ACCOUNT */}
            <button
              type="button"
              className="demo-account-button"
              onClick={handleDemoLogin}
              disabled={isBusy}
              title="Log in to a fully prepared demo workspace with sample data"
              aria-label="Try Demo Account"
            >
              <div className="demo-content-wrap">
                <div className="demo-icon-badge">
                  <Sparkles size={16} aria-hidden="true" />
                </div>
                <div>
                  <strong className="demo-title">
                    Try Demo Account
                  </strong>
                  <span className="demo-subtitle">
                    Preloaded portfolio data & charts
                  </span>
                </div>
              </div>

              {actionLoading === "demo" ? (
                <Loader2 size={16} className="auth-spinner demo-action-icon" />
              ) : (
                <ArrowRight size={16} className="demo-action-icon" />
              )}
            </button>

            {/* CONTINUE AS GUEST */}
            <button
              type="button"
              className="guest-access-button"
              onClick={handleGuestLogin}
              disabled={isBusy}
              title="Explore the application as a guest (temporary session, no account needed)"
              aria-label="Continue as Guest"
            >
              <div className="guest-content-wrap">
                <div className="guest-icon-badge">
                  <Compass size={16} aria-hidden="true" />
                </div>
                <div>
                  <strong className="guest-title">
                    Continue as Guest
                  </strong>
                  <span className="guest-subtitle">
                    Explore interface without saving
                  </span>
                </div>
              </div>

              {actionLoading === "guest" ? (
                <Loader2 size={16} className="auth-spinner guest-action-icon" />
              ) : (
                <ArrowRight size={16} className="guest-action-icon" />
              )}
            </button>
          </div>

          {/* TOGGLE FOOTER */}
          <p className="auth-footer">
            {mode === "login"
              ? "Don't have an account?"
              : "Already have an account?"}

            <button
              type="button"
              onClick={() =>
                switchMode(
                  mode === "login"
                    ? "signup"
                    : "login"
                )
              }
              disabled={isBusy}
            >
              {mode === "login"
                ? "Create one"
                : "Sign in"}
            </button>
          </p>

        </div>

        {/* POLICIES & SECURITY NOTICE */}
        <p className="auth-note">
          Guest sessions are temporary and data is not retained after the browser session. Demo accounts contain isolated portfolio samples.
        </p>

      </div>
    </div>
  );
}
