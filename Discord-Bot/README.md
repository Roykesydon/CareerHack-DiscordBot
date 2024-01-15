## Development (Discord Bot)

- Clone this repo
    ```shell
    $ cd Discord-Bot
    ```
- Install the Python dependencies
    ```shell
    $ pip install -r requirements.txt
    ```
- Write `./config.json`
    - You need to apply discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
- Run the code
    ```shell
    $ python main.py
    ```
- Look at [Developer Guide](docs/DEVELOPER.md) for more details about how to start developing this repository.
- Refer to [Contributing Guidelines](CONTRIBUTING.md) for the conventions and rules that contributors should follow.

## Project Structure

```shell
.
├── README.md # introduce this project
├── assets 
│   └── logo.png
├── config.example.json
├── config.json
├── core # business logic
│   ├── commands # all coomands
│   │   ├── description.py
│   │   ├── help.py
│   │   └── upload.py
│   ├── config.py # config and language loader
│   ├── database.py # database connection
│   ├── events # all events
│   │   └── directly_chat.py
│   └── message.py # message handler
├── lang # language files
│   └── en.json
├── main.py # program entry point
└── storage # save uploaded files
```