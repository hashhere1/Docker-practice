import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Scope needed to upload and manage files created by this app
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main():
  client_secret_path = "credentials/client_secret.json"
  token_path = "credentials/token.json"

  if not os.path.exists(client_secret_path):
    print(f"Error: {client_secret_path} not found!")
    return

  flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
  # Opens a local webserver and pops open your browser
  creds = flow.run_local_server(port=0)

  with open(token_path, "w") as token_file:
    token_file.write(creds.to_json())

  print(f"Successfully created {token_path}!")


if __name__ == "__main__":
  main()