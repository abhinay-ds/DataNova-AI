import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Loader2,
  LockKeyhole,
  Mail,
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
    isAuthenticated,
  } = useAuth();

  const [mode, setMode] = useState("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
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
          "Authentication failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-shell">

        <div className="auth-brand">
          <Link to="/">
            <BrandLogo className="login-logo" />
          </Link>
        </div>

        <div className="auth-card">

          <div className="auth-heading">
            <span className="auth-eyebrow">
              {mode === "login"
                ? "Welcome back"
                : "Get started"}
            </span>

            <h1>
              {mode === "login"
                ? "Sign in to DataNova"
                : "Create your DataNova account"}
            </h1>

            <p>
              {mode === "login"
                ? "Continue your data analysis workspace."
                : "Create an account and start analyzing your data."}
            </p>
          </div>

          <div className="auth-tabs">
            <button
              type="button"
              className={
                mode === "login"
                  ? "auth-tab active"
                  : "auth-tab"
              }
              onClick={() => switchMode("login")}
            >
              Login
            </button>

            <button
              type="button"
              className={
                mode === "signup"
                  ? "auth-tab active"
                  : "auth-tab"
              }
              onClick={() => switchMode("signup")}
            >
              Sign up
            </button>
          </div>

          {error && (
            <div className="auth-error" role="alert">
              {error}
            </div>
          )}

          <form
            className="auth-form"
            onSubmit={handleSubmit}
          >

            {mode === "signup" && (
              <label className="auth-field">
                <span>Full name</span>

                <div className="auth-input-wrap">
                  <UserRound size={18} />

                  <input
                    type="text"
                    value={fullName}
                    onChange={(event) =>
                      setFullName(event.target.value)
                    }
                    placeholder="Your name"
                    autoComplete="name"
                    disabled={loading}
                  />
                </div>
              </label>
            )}

            <label className="auth-field">
              <span>Email address</span>

              <div className="auth-input-wrap">
                <Mail size={18} />

                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  placeholder="you@example.com"
                  autoComplete="email"
                  disabled={loading}
                  required
                />
              </div>
            </label>

            <label className="auth-field">
              <span>Password</span>

              <div className="auth-input-wrap">
                <LockKeyhole size={18} />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  placeholder="Enter your password"
                  autoComplete={
                    mode === "login"
                      ? "current-password"
                      : "new-password"
                  }
                  disabled={loading}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      (current) => !current
                    )
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                  disabled={loading}
                >
                  {showPassword ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>
              </div>
            </label>

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2
                    size={18}
                    className="auth-spinner"
                  />
                  {mode === "login"
                    ? "Signing in..."
                    : "Creating account..."}
                </>
              ) : (
                <>
                  {mode === "login"
                    ? "Sign in"
                    : "Create account"}

                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

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
            >
              {mode === "login"
                ? "Create one"
                : "Sign in"}
            </button>
          </p>

        </div>

        <p className="auth-note">
          Your DataNova workspace is protected by
          authenticated access.
        </p>

      </div>
    </div>
  );
}