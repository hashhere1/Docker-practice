const API_BASE_URL = "http://127.0.0.1:8000";

export async function getGoogleDriveAuthUrl(jwtToken) {
  const response = await fetch(`${API_BASE_URL}/google-drive/connect`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${jwtToken}`,
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