const API_BASE_URL = "http://127.0.0.1:8000";

export async function getGoogleDriveAuthUrl(mode = "all", jwtToken = null) {
  const token = jwtToken || localStorage.getItem("token");

  if (!token) {
    throw new Error("No active session found. Please log in first.");
  }

  const response = await fetch(`${API_BASE_URL}/google-drive/connect?mode=${mode}`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data.authorization_url;
}