# Hacker-Rank-Discord-Bot

## Development

- Clone this repo
    ```shell
    $ git clone https://github.com/Roykesydon/Hacker-Rank-Discord-Bot.git
    ```
- Install the Python dependencies
    ```shell
    $ pip install -r requirements.txt
    ```
- Write `./config.json`
    - You need to apply discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
    - ```cp config.example.json config.json```
- Write `.env`
    - You need to apply OpenAI API and HuggingFace API token from [OpenAI](https://openai.com/blog/openai-api) and [HuggingFace](https://huggingface.co/inference-api)
    - ```cp .env.example .env```
- Run the code
    ```shell
    $ python main.py
    ```
- Look at [Developer Guide](docs/DEVELOPER.md) for more details about how to start developing this repository.
- Refer to [Contributing Guidelines](docs/CONTRIBUTING.md) for the conventions and rules that contributors should follow.

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


## how to maintain this repo
每次增修內容前請依循下列流程進行：
1. Pull origin/develop 最新版本
    ```shell
    $ git pull origin develop
    ```
2. 在 local 新增 branch 並切換
    ```shell
    $ git checkout -b <NEW_BRANCH_NAME>
    ```
3. 編輯完成後進行 commit
    ```shell
    $ git add .
    $ git commit -m "COMMIT_MSG"
    ```
4. 回到 develop 再次獲取 origin/develop 的最新版本、與自己的修正合併並修正出現的 conflict
    ```shell
    $ git checkout develop
    $ git pull
    $ git checkout <NEW_BRANCH_NAME>
    $ git rebase develop
    ```
5. 將新 branch 的修正與 develop 合併並 push 到 Github
    ```shell
    $ git checkout develop
    $ git merge <NEW_BRANCH_NAME>
    $ git push
    ```
