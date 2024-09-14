import typer
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from typing import Optional, Dict
from rich.console import Console
from rich.syntax import Syntax
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import tempfile
import subprocess
import os
import json

CONFIG_FILE = os.path.expanduser("~/.aigit/model.json")


def get_config_input() -> Dict[str, str]:
    settings = {
        'model': typer.prompt("请输入模型名称"),
        'base_url': typer.prompt("请输入基础URL"),
        'temperature': typer.prompt("请输入温度值", type=float),
        'api_key': typer.prompt("请输入API密钥"),
    }
    return settings

def save_config(configure: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    with open(CONFIG_FILE, 'w') as f:
        json.dump(configure, f, indent=2)

def load_config() -> Dict[str, str]:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def get_model():
    configure = load_config()
    return ChatOpenAI(
        model=configure.get('model', ""),
        base_url=configure.get('base_url', ''),
        temperature=configure.get('temperature', 0.2),
        api_key=configure.get('api_key', ''),
    )


system_prompt = '''
Craft clear and concise commit messages following the Conventional Commits standard format for git. When presented with a git diff summary, your task is to convert it into a useful commit message and add a brief description of the changes made, ensuring that lines are not longer than 74 characters. 
Your commit message should describe the nature and purpose of the changes in a comprehensive, informative, and concise manner. The commit message should follow the format: <type>(<scope>): <subject>, starting the <subject> with an emoji that appropriately describes the content, and an optional body for more detailed changes or multiple changes listed briefly in bullet points. Keep the content concise and to the point.
Answer all my questions in {language}.
'''


parser = StrOutputParser()

app = typer.Typer()
console = Console()

def beautify_diff(diff_output: str) -> None:
    syntax = Syntax(diff_output, "diff", line_numbers=True, word_wrap=True, indent_guides=False, theme="monokai")
    console.print(syntax)

def get_git_diff(repo: Repo, staged: bool = False, file_path: Optional[str] = None):
    exclude_pattern = ":!*.lock"
    if staged:
        return repo.git.diff('--staged', file_path, exclude_pattern)
    else:
        return repo.git.diff(file_path, exclude_pattern)

def edit_commit_message(initial_message: str) -> str:
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".tmp", delete=False) as tf:
        tf.write(initial_message)
        tf.flush()
        tf_name = tf.name

    editor = os.environ.get('EDITOR', 'vim')
    subprocess.call([editor, tf_name])

    with open(tf_name, 'r') as tf:
        edited_message = tf.read().strip()

    os.unlink(tf_name)
    return edited_message

def commit_changes(repo: Repo, commit_message: str):
    repo.git.add(A=True)
    repo.index.commit(commit_message)

def check_config_exists() -> bool:
    _config = load_config()
    return all(key in _config for key in ['model', 'base_url', 'temperature', 'api_key'])

@app.command()
def config():
    """配置AI提交助手"""
    configure = get_config_input()
    save_config(configure)
    typer.echo("配置已保存")


@app.command()
def diff(
        staged: bool = typer.Option(False, "--staged", "-s", help="显示暂存的更改"),
        file_path: Optional[str] = typer.Option(None, "--file", "-f", help="指定文件路径"),
):
    try:
        repo = Repo('.')
        diff_output = get_git_diff(repo, staged, file_path)

        if not diff_output:
            typer.echo("没有检测到更改。")
        else:
            beautify_diff(diff_output)

    except InvalidGitRepositoryError:
        typer.echo("错误：当前目录不是有效的Git仓库。", err=True)
    except GitCommandError as e:
        typer.echo(f"Git命令执行错误：{str(e)}", err=True)


@app.command()
def commit(
        staged: bool = typer.Option(False, "--staged", "-s", help="显示暂存的更改"),
        file_path: Optional[str] = typer.Option(None, "--file", "-f", help="指定文件路径"),
        language: str = typer.Option("English", "--lang", "-l", help="设置语言（English/Chinese）"),

):
    if not check_config_exists():
        typer.echo("错误：未找到配置信息。请先运行 'aigit config' 命令进行配置。")
        raise typer.Exit(code=1)
    """
    显示当前Git仓库的代码更改
    """
    try:
        repo = Repo('.')
        diff_output = get_git_diff(repo, staged, file_path)

        if not diff_output:
            typer.echo("没有检测到更改。")
        else:
            message_content = '''
git diff summary:
{diff_summary}
'''

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", message_content),
            ])

            messages = prompt.invoke({"language": language, 'diff_summary': diff_output})

            model = get_model()

            result = model.invoke(messages)
            initial_commit_message = parser.invoke(result)
            initial_commit_message = initial_commit_message.strip('```')
            initial_commit_message = initial_commit_message.strip()

            typer.echo("AI 生成的提交信息：")
            typer.echo(initial_commit_message)
            typer.echo("\n请编辑提交信息，保存并关闭编辑器以继续。")

            edited_message = edit_commit_message(initial_commit_message)

            typer.echo("编辑后的提交信息：")
            typer.echo(edited_message)

            if typer.confirm("确认提交这些更改？"):
                commit_changes(repo, edited_message)
                typer.echo("更改已成功提交！")
            else:
                typer.echo("提交已取消。")

    except InvalidGitRepositoryError:
        typer.echo("错误：当前目录不是有效的Git仓库。", err=True)
    except GitCommandError as e:
        typer.echo(f"Git命令执行错误：{str(e)}", err=True)


if __name__ == "__main__":
    app()
