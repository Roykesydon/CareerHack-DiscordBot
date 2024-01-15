# Hacker-Rank-Discord-Bot

## Development
-   Clone this repo
    ```shell
    $ git clone https://github.com/Roykesydon/Hacker-Rank-Discord-Bot.git
    $ cd Hacker-Rank-Discord-Bot/
    ```

- Look at [Developer Guide](docs/DEVELOPER.md) for more details about how to start developing this repository.
- Refer to [Contributing Guidelines](CONTRIBUTING.md) for the conventions and rules that contributors should follow.


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
4. 回到 main 再次獲取 origin/develop 的最新版本、與自己的修正合併並修正出現的 conflict
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