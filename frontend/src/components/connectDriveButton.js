import { getGoogleDriveAuthUrl } from "../api/driveApi.js";

export function initConnectButton() {
  const modeSelect = document.getElementById("permissionMode");
  const connectBtn = document.getElementById("connectBtn");
  const errorBox = document.getElementById("errorMessage");

  connectBtn.addEventListener("click", async () => {
    errorBox.textContent = "";

    const selectedMode = modeSelect ? modeSelect.value : "all";

    try {
      connectBtn.disabled = true;
      connectBtn.textContent = "Redirecting to Google...";

      const authUrl = await getGoogleDriveAuthUrl(selectedMode);

      window.location.href = authUrl;
    } catch (err) {
      errorBox.textContent = err.message || "Failed to initiate Google Drive connection.";
      connectBtn.disabled = false;
      connectBtn.textContent = "Connect to Google Drive";
    }
  });
}