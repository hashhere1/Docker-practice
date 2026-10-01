import { getGoogleDriveAuthUrl } from "../api/driveApi.js";

export function initConnectButton() {
  const tokenInput = document.getElementById("jwtToken");
  const connectBtn = document.getElementById("connectBtn");
  const errorBox = document.getElementById("errorMessage");

  connectBtn.addEventListener("click", async () => {
    const token = tokenInput.value.trim();
    errorBox.textContent = "";

    if (!token) {
      errorBox.textContent = "Please enter your FastAPI JWT token.";
      return;
    }

    try {
      connectBtn.disabled = true;
      connectBtn.textContent = "Redirecting to Google...";

      // 1. Get the Google consent URL from your FastAPI backend
      const authUrl = await getGoogleDriveAuthUrl(token);

      // 2. Perform top-level window redirect to Google consent screen
      window.location.href = authUrl;
    } catch (err) {
      errorBox.textContent = err.message || "Failed to initiate Google Drive connection.";
      connectBtn.disabled = false;
      connectBtn.textContent = "Connect to Google Drive";
    }
  });
}