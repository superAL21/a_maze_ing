from maze_generator import MazeGenerator
from parser import config_parser, converter, config_validator
from typing import Any
import sys
import time
import random
import re


def menu(data: dict[str, Any]) -> None:
    """Run the interactive maze menu loop.

    Generates an initial maze from the given config and then lets the
    user regenerate it (with an optional seed and animation), show or
    hide the solution path, change the colour theme, and export a
    snapshot of the maze to a file.

    Args:
        data: The validated configuration dictionary.
    """
    maze = MazeGenerator(data)
    maze.animate = False
    maze.stamp_42()
    maze.generate()
    if not maze.perfect:
        maze.add_loops()
        maze.braid()
    maze.find_path()
    maze.write_file()
    show_solution = False
    current_theme = "Default"

    while True:
        print("\033[2J\033[3J\033[H", end="")
        maze.display(show_path=show_solution)
        print()
        print("    \033[1;38;2;0;180;216mA-Maze-ing\033[0m")
        print()
        print(f"\033[38;2;0;180;216mPlaying with seed"
              f" \033[38;2;177;128;240m{maze.seed}\033[0m")
        print()
        time.sleep(0.1)

        print("\033[1;38;2;0;180;216m1.\033[0m \033[38;2;177;128;240m"
              "Regenerate maze\033[0m")
        print("\033[1;38;2;0;180;216m2.\033[0m \033[38;2;177;128;240mShow/hide"
              " path\033[0m")
        print("\033[1;38;2;0;180;216m3.\033[0m \033[38;2;177;128;240m"
              "Change colours\033[0m")
        print("\033[1;38;2;0;180;216m4.\033[0m \033[38;2;177;128;240m"
              "Snapshot\033[0m")
        print("\033[1;38;2;0;180;216m5.\033[0m \033[38;2;177;128;240m"
              "Exit\033[0m")
        print()
        time.sleep(0.1)

        choice = input("\033[1;38;2;0;180;216mOption: \033[0m")

        if choice == "1":
            seed_input = input(
                "\033[38;2;177;128;240mSeed (Enter for random): \033[0m"
                )
            if seed_input.strip() == "":
                seed = random.randint(0, 999999)
            else:
                try:
                    seed = int(seed_input)
                except ValueError:
                    seed = None
                    print("\033[38;2;0;180;216mInvalid data type,"
                          " seed must be a valid number\033[0m")
                    input(
                        "\033[38;2;177;128;240mPress ["
                        "\033[1;38;2;0;180;216mEnter"
                        "\033[0m\033[38;2;177;128;240m] "
                        "to continue: \033[0m"
                    )
            anim_input = input(
                "\033[38;2;177;128;240mAnimate generation? (y/N): \033[0m"
            )

            maze = MazeGenerator(data, seed)
            maze.apply_theme(current_theme)
            maze.animate = (anim_input.strip().lower() == "y")
            maze.stamp_42()
            maze.generate()
            maze.animate = False
            if not maze.perfect:
                maze.add_loops()
                maze.braid()
            maze.find_path()
            maze.write_file()
            show_solution = False

        elif choice == "2":
            if show_solution:
                show_solution = False
            else:
                maze.animate_path(0.07)
                show_solution = True
                print()
                input(
                    "\033[38;2;177;128;240mPress ["
                    "\033[1;38;2;0;180;216mEnter"
                    "\033[0m\033[38;2;177;128;240m] "
                    "to continue: \033[0m"
                )

        elif choice == "3":
            while True:

                print("\033[2J\033[3J\033[H", end="")
                print("\033[1;38;2;0;180;216m1.\033[0m \033[38;2;177;128;240m"
                      "Default\033[0m")
                print("\033[1;38;2;0;180;216m2.\033[0m \033[38;2;177;128;240m"
                      "Cyberpunk\033[0m")
                print("\033[1;38;2;0;180;216m3.\033[0m \033[38;2;177;128;240m"
                      "Barbie\033[0m")
                print("\033[1;38;2;0;180;216m4.\033[0m \033[38;2;177;128;240m"
                      "Oasis\033[0m")
                print("\033[1;38;2;0;180;216m5.\033[0m \033[38;2;177;128;240m"
                      "Nebula\033[0m")
                print("\033[1;38;2;0;180;216m6.\033[0m \033[38;2;177;128;240m"
                      "Arctic\033[0m")
                print("\033[1;38;2;0;180;216m7.\033[0m \033[38;2;177;128;240m"
                      "Back to menu\033[0m")
                print()

                theme_choice = input(
                    "\033[1;38;2;0;180;216mOption: \033[0m"
                )

                if theme_choice == "7":
                    break

                if theme_choice in ["1", "2", "3", "4", "5", "6"]:
                    names = list(maze.theme.keys())
                    name = names[int(theme_choice) - 1]
                    maze.apply_theme(name)
                    current_theme = name
                    break

        elif choice == "4":
            filename_input = input(
                "\n\033[38;2;177;128;240mFilename "
                "(Enter for 'maze_art.txt'): \033[0m"
                ).strip()
            if filename_input == "":
                filename = "maze_art.txt"
            else:
                filename = (
                    filename_input if filename_input.endswith(".txt")
                    else f"{filename_input}.txt"
                )

            protected = {"requirements.txt", "config.txt", data["OUTPUT_FILE"]}
            if not re.fullmatch(r"[A-Za-z0-9_-]+\.txt", filename):
                print(
                    "\n\033[1;38;2;255;50;50m[ERROR]\033[0m Invalid filename. "
                    "Use only letters, digits, '_' or '-'."
                )
            elif filename in protected:
                print(
                    "\n\033[1;38;2;255;50;50m[ERROR]\033[0m Cannot overwrite "
                    f"protected file: '{filename}'"
                )
            else:
                maze.export_ansi_art(filename, show_path=show_solution)

            input(
                "\n\033[38;2;177;128;240mPress [Enter] to continue... \033[0m"
                )

        elif choice == "5":
            break

        else:
            print(
                "\n\033[1;38;2;255;50;50m[ERROR]"
                "\033[0m Invalid choice."
            )
            input(
                "\033[38;2;177;128;240mPress ["
                "\033[1;38;2;0;180;216mEnter"
                "\033[0m\033[38;2;177;128;240m] "
                "to continue: \033[0m"
            )


def main() -> None:
    """Entry point: read the config file and start the menu.

    Expects exactly one command-line argument, the path to the config
    file. Parses, converts and validates it, then launches the menu.
    Configuration and runtime errors are caught and reported without
    crashing.
    """

    if (len(sys.argv) != 2):
        print("[INFO] Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        config_file = sys.argv[1]
        data = config_parser(config_file)
        data = converter(data)
        if config_validator(data, config_file):
            menu(data)
        else:
            print("Error. Try again later")

        print(
            "\033[38;2;0;180;216mThanks for playing"
            " \033[38;2;177;128;240mA-MAZE-ING!\033[0m"
            )
    except (ValueError, KeyError, OSError) as error:
        print(f"\033[1;38;2;255;50;50m[CONFIG ERROR]\033[0m {error}")

    except (KeyboardInterrupt, EOFError):
        print(
            "\n\n\033[1;38;2;255;255;0m[INFO]"
            "\033[0m\033[38;2;177;128;240m Ending the game. Bye-Bye!\033[0m"
        )
        print("\033[?25h", end="")
        sys.exit(0)


if __name__ == "__main__":
    main()
