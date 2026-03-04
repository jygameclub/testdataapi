"""
Slack Bot — 监听频道中上传的 anubis*.zip 文件，
自动处理数据、推送到 GitHub、回复 url.txt 内容。

用法:
  1. 复制 .env.example 为 .env 并填入 token
  2. pip install -r requirements.txt
  3. python slack_bot.py
"""

import os
import re
import subprocess
import tempfile

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from process_anubis_zip import process_zip

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def is_anubis_zip(filename: str) -> bool:
    """文件名含 anubis 且以 .zip 结尾。"""
    return "anubis" in filename.lower() and filename.lower().endswith(".zip")


def download_file(client, url: str, dest: str):
    """用 Bot Token 下载 Slack 文件到本地路径。"""
    import urllib.request

    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"}
    )
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def git_push(message: str):
    """git add + commit + push（在仓库目录执行）。"""
    subprocess.run(["git", "add", "."], cwd=SCRIPT_DIR, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=SCRIPT_DIR, check=True)
    subprocess.run(["git", "push"], cwd=SCRIPT_DIR, check=True)


@app.event("message")
def handle_message(event, client, say):
    # 只处理含文件的消息
    files = event.get("files")
    if not files:
        return

    for file_info in files:
        filename = file_info.get("name", "")
        if not is_anubis_zip(filename):
            continue

        channel = event["channel"]
        user = event.get("user", "unknown")
        thread_ts = event.get("ts")

        say(
            text=f"检测到 `{filename}`，正在处理...",
            channel=channel,
            thread_ts=thread_ts,
        )

        try:
            # 下载 zip 到临时文件
            download_url = file_info["url_private_download"]
            tmp_zip = os.path.join(tempfile.gettempdir(), filename)
            download_file(client, download_url, tmp_zip)

            # 处理数据
            date_dir, url_file, count = process_zip(tmp_zip)

            # 推送到 GitHub
            git_push(f"Add anubis data {date_dir}")

            # 读取 url.txt 内容并回复
            with open(url_file, "r", encoding="utf-8") as f:
                url_content = f.read().strip()

            say(
                text=f"处理完成！共 {count} 个文件，目录: `anubisdate/{date_dir}/`\n\n```\n{url_content}\n```",
                channel=channel,
                thread_ts=thread_ts,
            )

            # 清理临时文件
            os.remove(tmp_zip)

        except Exception as e:
            say(
                text=f"处理失败: {e}",
                channel=channel,
                thread_ts=thread_ts,
            )


if __name__ == "__main__":
    print("Slack Bot 已启动，等待 anubis zip 文件...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
