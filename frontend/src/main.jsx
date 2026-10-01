import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";

import { ThemeProvider } from "./context/ThemeContext";
import { AuthProvider } from "./context/AuthContext";
import { ProjectProvider } from "./context/ProjectContext";
import { DatasetProvider } from "./context/DatasetContext";
import { ChatProvider } from "./context/ChatContext";

import "./styles/globals.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <ProjectProvider>
          <DatasetProvider>
            <ChatProvider>
              <App />
            </ChatProvider>
          </DatasetProvider>
        </ProjectProvider>
      </AuthProvider>
    </ThemeProvider>
  </StrictMode>
);