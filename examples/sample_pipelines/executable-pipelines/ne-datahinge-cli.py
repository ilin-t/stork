import argparse
import importlib.util
import json
import os
import sys
import readline
import asyncio
import logging
import configparser

from typing import List, Dict, Any, Tuple
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import ProgressBar
from pygments.lexers.shell import BashLexer
from traceback import format_exc
from collections import deque
from itertools import chain

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read configuration file
config = configparser.ConfigParser()
config.read("config.ini")


def completer(text: str, state: int) -> str:
    available_commands = [name for name, func in globals().items() if callable(func) and not name.startswith("_")]
    options = [cmd for cmd in available_commands if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None


class ModuleCompleter(Completer):

    def __init__(self, scripts):
        self.scripts = scripts

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        matches = [mod for mod in self.scripts if mod.startswith(word_before_cursor)]
        for m in matches:
            yield Completion(m, -len(word_before_cursor))


async def run_script(script, arguments, background=False):
    if not background:
        with ProgressBar() as pb:
            for i in pb(range(100)):
                await asyncio.sleep(0.005)

    main_func = script["module"].main
    if asyncio.iscoroutinefunction(main_func):
        await main_func(arguments)
    else:
        main_func(arguments)

def load_scripts() -> Dict[str, Dict[str, Any]]:
    sys.path.append(os.path.join(os.getcwd(), "scripts"))

    scripts = {}
    with open("modules.json") as f:
        modules_data = json.load(f)

    error_logger = logging.getLogger('module_error')
    error_logger.setLevel(logging.ERROR)
    handler = logging.FileHandler('module-error.log')
    error_logger.addHandler(handler)

    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "scripts")):
        for file_name in files:
            if file_name.endswith(".py"):
                module_name = file_name[:-3]
                file_path = os.path.join(root, file_name)
                module_data = modules_data.get(module_name, {})
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                except Exception as e:
                    error_msg = f"Error: Could not import module {module_name}. {str(e)}"
                    print(error_msg)
                    error_logger.error(error_msg)
                    continue

                scripts[module_name] = {
                    "module": module,
                    "title": module_data.get("title", module_name),
                    "meta_title": module_data.get("meta_title", module_name),
                    "description": module_data.get("description", ""),
                    "args": module_data.get("args", []),
                }
                print(f"Loaded module {module_name}")

                if module_name == "gh_repo_downloader":
                    scripts[module_name]["module"].main = module.main

    return scripts
    
def list_commands(scripts):
    print("Available commands:")
    print("===================")
    print("exit - Exit the program")
    print("module [module_name] [args] - Run a module with the specified name and arguments")
    print("reload - Reload module data")
    print("info [module_name] - Get information about a module")
    print("interactive [module_name] - Run a module in interactive mode")
    print("config [key] [value] - Get or set a configuration value")
    print("alias [alias] [command] - Create, list, or execute command aliases")
    print("help - Show this help message\n")
    print("Available modules:")
    print("===================")
    for module_name, script in scripts.items():
        print(f"{module_name} - {script['description']}")
    print("\nUse 'module [module_name] --help' for module usage instructions.")

def DataHingeCLI() -> None:
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    print("Welcome to Ivan's Data CLI Tool!")
    scripts = load_scripts()
    aliases = {}

    session = PromptSession(
        history=FileHistory(".cli_tool_history"),
        auto_suggest=AutoSuggestFromHistory(),
        lexer=PygmentsLexer(BashLexer),
    )

    while True:
        try:
            user_input = session.prompt("Enter a command: ", completer=ModuleCompleter(scripts)).split()
            if not user_input:
                continue 
            command = user_input[0]
            arguments = user_input[1:]

            if command == "exit":
                break
            elif command == "help":
                list_commands(scripts)

            if command == "module":
                if len(arguments) == 0:
                    print("Error: Module name is missing.")
                    continue

                module_name = arguments[0]
                if module_name in scripts:
                    try:
                        script = scripts[module_name]
                        asyncio.run(run_script(script, arguments[1:]))
                    except KeyboardInterrupt:
                        print("\nExiting...")
                    except SystemExit as e:
                        print(f"Error: {e}")
                        print(f"Usage: module {module_name} {' '.join(script['args'])}")
                    except argparse.ArgumentError as e:
                        print(f"Error: {e}")
                        print(f"Usage: module {module_name} {' '.join(script['args'])}")
                    except Exception as e:
                        print(f"Error: {e}")
                        logger.error(format_exc())
                else:
                    print(f"Error: Module {module_name} not found.")
            elif command == "reload":
                scripts = load_scripts()
            elif command == "info":
                if len(arguments) == 0:
                    print("Error: Module name is missing.")
                    continue

                module_name = arguments[0]
                if module_name in scripts:
                    script = scripts[module_name]
                    print(f"{script['title']}")
                    print(f"  Description: {script['description']}")
                    print(f"  Usage: module {module_name} {' '.join(script['args'])}")
                else:
                    print(f"Error: Module {module_name} not found.")
            elif command == "interactive":
                if len(arguments) == 1:
                    module_name = arguments[0]
                    if module_name in scripts:
                        script = scripts[module_name]
                        if hasattr(script["module"], "interactive"):
                            try:
                                script["module"].interactive()
                            except Exception as e:
                                print(f"Error: {e}")
                                logger.error(format_exc())
                        else:
                            print(f"Error: Module {module_name} does not support interactive mode.")
                    else:
                        print(f"Error: Module {module_name} not found.")
                else:
                    print("Error: Interactive command requires exactly one module name as an argument.")
            elif command == "config":
                if len(arguments) == 0:
                    for section in config.sections():
                        print(f"[{section}]")
                        for key, value in config.items(section):
                            print(f"{key} = {value}")
                        print()
                elif len(arguments) == 1:
                    key = arguments[0]
                    if key in config.defaults():
                        print(f"{key} = {config.get('DEFAULT', key)}")
                    else:
                        print(f"Error: Key '{key}' not found in configuration.")
                elif len(arguments) == 2:
                    key, value = arguments
                    if key in config.defaults():
                        config.set("DEFAULT", key, value)
                        with open("config.ini", "w") as configfile:
                            config.write(configfile)
                        print(f"Configuration updated: {key} = {value}")
                    else:
                        print(f"Error: Key '{key}' not found in configuration.")
                else:
                    print("Error: Config command requires zero, one or two arguments.")
            elif command == "alias":
                if len(arguments) == 0:
                    if aliases:
                        for alias, command in aliases.items():
                            print(f"{alias} -> {command}")
                    else:
                        print("No aliases defined.")
                elif len(arguments) == 1:
                    alias = arguments[0]
                    if alias in aliases:
                        print(f"{alias} -> {aliases[alias]}")
                    else:
                        print(f"Error: Alias '{alias}' not found.")
                elif len(arguments) == 2:
                    alias, command = arguments
                    aliases[alias] = command
                    print(f"Alias added: {alias} -> {command}")
                else:
                    print("Error: Alias command requires zero, one, or two arguments.")
            else:
                if command in aliases:
                    alias_command = aliases[command]
                    user_input = f"{alias_command} {' '.join(arguments)}".split()
                    command = user_input[0]
                    arguments = user_input[1:]
                else:
                    print("Available modules:")
                    for module_name, script in scripts.items():
                        print(f"{module_name} - {script['description']}")
                    print("\nUse 'module [module_name] --help' for module usage instructions.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    DataHingeCLI()