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

from process_anubis_zip import process_zip as process_anubis
from process_ox_txt import process_file as process_ox
from process_tiger_txt import process_file as process_tiger

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def is_anubis_zip(filename: str) -> bool:
    """文件名含 anubis 且以 .zip 结尾。"""
    return "anubis" in filename.lower() and filename.lower().endswith(".zip")


def is_ox_file(filename: str) -> bool:
    """文件名含 ox 且以 .txt 或 .zip 结尾。"""
    lower = filename.lower()
    return "ox" in lower and (lower.endswith(".txt") or lower.endswith(".zip"))


def is_tiger_file(filename: str) -> bool:
    """文件名含 tiger 且以 .txt 或 .zip 结尾。"""
    lower = filename.lower()
    return "tiger" in lower and (lower.endswith(".txt") or lower.endswith(".zip"))


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
        channel = event["channel"]
        thread_ts = event.get("ts")

        # 判断文件类型
        if is_anubis_zip(filename):
            game_type = "anubis"
        elif is_ox_file(filename):
            game_type = "ox"
        elif is_tiger_file(filename):
            game_type = "tiger"
        else:
            continue

        say(
            text=f"检测到 `{filename}`，正在处理 ({game_type})...",
            channel=channel,
            thread_ts=thread_ts,
        )

        try:
            # 下载文件到临时目录
            download_url = file_info["url_private_download"]
            tmp_file = os.path.join(tempfile.gettempdir(), filename)
            download_file(client, download_url, tmp_file)

            # 处理数据
            if game_type == "anubis":
                date_dir, url_file, count = process_anubis(tmp_file)
                data_dir_name = "anubisdate"
            elif game_type == "ox":
                date_dir, url_file, count = process_ox(tmp_file)
                data_dir_name = "oxdate"
            else:
                date_dir, url_file, count = process_tiger(tmp_file)
                data_dir_name = "tigerdate"

            # 推送到 GitHub
            git_push(f"Add {game_type} data {date_dir}")

            # 读取 url.txt 内容并回复
            with open(url_file, "r", encoding="utf-8") as f:
                url_content = f.read().strip()

            say(
                text=f"处理完成！共 {count} 个文件，目录: `{data_dir_name}/{date_dir}/`\n\n```\n{url_content}\n```",
                channel=channel,
                thread_ts=thread_ts,
            )

            # 清理临时文件
            os.remove(tmp_file)

        except Exception as e:
            say(
                text=f"处理失败: {e}",
                channel=channel,
                thread_ts=thread_ts,
            )


if __name__ == "__main__":
    print("Slack Bot 已启动，等待 anubis/ox/tiger 文件...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
