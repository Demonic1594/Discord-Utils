# WebSocket and HTTP-based Version
This version features a WebSocket and HTTP-based version that authenticates Discord accounts through HTTP requests. It verifies token validity by fetching user information from the Discord API. Once authenticated, the utility establishes a WebSocket connection to manage real-time presence updates. This allows for continuous interaction with Discord's gateway, enabling users to set custom statuses and maintain online presence effectively. The utility is designed to handle multiple accounts concurrently, incorporating robust logging and error management to ensure smooth operation.

# Features
- **Token Authentication**: Validates Discord tokens through HTTP requests to ensure they are active and authorized.
- **Real-time Presence Management**: Uses WebSocket to maintain continuous communication with Discord, enabling real-time updates of online status and custom statuses.
- **Multi-account Support**: Capable of managing multiple Discord accounts simultaneously using threading for efficient execution.
- **Custom Status Updates**: Allows users to set and update custom statuses for their accounts.
- **Heartbeat Management**: Sends periodic heartbeat messages to maintain the WebSocket connection and prevent timeouts.
- **Robust Error Handling**: Includes comprehensive error handling for connection issues, invalid tokens, and unexpected exceptions.
- **Colored Logging**: Features a colored logging system for easy reading of log messages, categorizing them by severity (INFO, ERROR, etc.).
- **Configuration Management**: Loads account details and settings from a JSON configuration file, simplifying setup and customization.
- **Graceful Shutdown**: Handles keyboard interrupts to allow for a clean shutdown, ensuring all threads and connections close properly.
- **Log File Generation**: Records all activities and errors in a log file for later review, aiding in debugging and monitoring.

# Usage
Clone the repository.
```
git clone https://github.com/Demonic1594/Discord-Utils.git
```
Locate to the directory.
```
cd Discord-Utils/Utilities/247Online
```
Choose which version, in this we go to version 1.
```
cd "Version 1"
```
Install the requirements.
```
pip install -r requirements.txt
```
Edit the config.json with your details.
+ Token - Your Discord User Token.
+ Status - Status you want to set, the options are; online, idle, dnd.
+ Custom Status - The custom status you want to add or can be left blank.
```py
{
  "accounts": [
    {
      "token": "DiscordUserToken1",
      "status": "online",
      "custom_status": "Your custom status 1"
    }
  ]
}
```
 + Simply add another section to add another account.
```py
{
  "accounts": [
    {
      "token": "DiscordUserToken1",
      "status": "online",
      "custom_status": "Your custom status 1"
    },
    {
      "token": "DiscordUserToken2",
      "status": "idle",
      "custom_status": "Your custom status 2"
    }
  ]
}
```
And finally, run the file.
```
python main.py
```

