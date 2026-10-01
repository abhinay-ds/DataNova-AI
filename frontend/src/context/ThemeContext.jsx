import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

const ThemeContext = createContext(null);

const STORAGE_KEY = "datanova-theme";

function getInitialTheme() {
  try {
    const savedTheme = localStorage.getItem(STORAGE_KEY);

    if (savedTheme === "dark" || savedTheme === "light") {
      return savedTheme;
    }
  } catch {
    // Ignore localStorage errors.
  }

  return "light";
}

function applyTheme(theme) {
  const root = document.documentElement;
  const body = document.body;

  root.setAttribute("data-theme", theme);
  root.classList.toggle("dark", theme === "dark");
  root.classList.toggle("light", theme === "light");

  body.setAttribute("data-theme", theme);
  body.classList.toggle("dark", theme === "dark");
  body.classList.toggle("light", theme === "light");

  body.style.background =
    theme === "dark" ? "#111827" : "#f7f9fc";

  body.style.color =
    theme === "dark" ? "#e5e7eb" : "#0f172a";
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(getInitialTheme);

  useEffect(() => {
    applyTheme(theme);

    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // Ignore localStorage errors.
    }
  }, [theme]);

  const setTheme = (nextTheme) => {
    const normalized =
      nextTheme === "dark" ? "dark" : "light";

    setThemeState(normalized);
  };

  const toggleTheme = () => {
    setThemeState((current) =>
      current === "dark" ? "light" : "dark"
    );
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        toggleTheme,
        isDark: theme === "dark",
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error(
      "useTheme must be used inside ThemeProvider"
    );
  }

  return context;
}