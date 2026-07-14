import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
  const [message, setMessage] = useState("Connecting...");
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    api.get("/")
      .then((response) => {
        setMessage(response.data.message);
      })
      .catch(() => {
        setMessage("Unable to connect to backend");
      });

    api.get("/health")
      .then((response) => {
        setStatus(response.data.status);
      })
      .catch(() => {
        setStatus("Offline");
      });
  }, []);

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f8fafc",
        fontFamily: "Arial",
      }}
    >
      <div
        style={{
          background: "white",
          padding: "40px",
          borderRadius: "15px",
          boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
          width: "500px",
          textAlign: "center",
        }}
      >
        <h1>DataNova AI</h1>

        <h3>{message}</h3>

        <p>
          Backend Status:
          {" "}
          <strong>{status}</strong>
        </p>

        <hr />

        <p>
          Milestone 4 Complete ✅
        </p>
      </div>
    </div>
  );
}

export default App;