# Name of the executable or main script
NAME        = amezing

# Python and Virtual Environment Configuration
PYTHON      = python3
VENV        = .venv
PIP         = $(VENV)/bin/pip
PY_VENV     = $(VENV)/bin/python

# Main Python script that runs your program
SRCS        = maze_generator.py cell.py parser.py a_maze_ing.py

# Default rule
all: $(NAME)

# Create the virtual environment and install dependencies if requirements.txt exists
$(VENV):
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@if [ -f requirements.txt ]; then \
		echo "Installing dependencies from requirements.txt..."; \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r requirements.txt; \
	fi

# Create a bridge executable script
$(NAME): $(VENV) $(SRCS)
	@echo "Generating executable $(NAME)..."
	@echo "#!/bin/bash" > $(NAME)
	@echo "source $(VENV)/bin/activate" >> $(NAME)
	@echo "$(PY_VENV) a_maze_ing.py \"\$$@\"" >> $(NAME)
	@chmod +x $(NAME)
	@echo "DONE! Now you can run the project using ./$(NAME)"

#Run the program with config.txt
run: $(NAME)
	@echo "Launching $(NAME) with config.txt..."
	@./$(NAME) config.txt

# Clean temporary Python files (__pycache__)
clean:
	@echo "Cleaning temporary Python files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf .mypy_cache

# Clean everything (including the virtual environment and the executable)
fclean: clean
	@echo "Removing virtual environment and executable..."
	@rm -rf $(VENV)
	@rm -f $(NAME)

# Rebuild everything from scratch
re: fclean all

# Install dependencies (via venv)
install: $(VENV)

# Debug: run the main script with py debugger(pdb)
debug: $(VENV)
	@echo "Launching $(NAME) with python debugger..."
	@$(PY_VENV) -m pdb a_maze_ing.py config.txt

# Lint: flake8 + mypy with the required flags
lint:
	@$(PY_VENV) -m flake8 --exclude=.venv,maze_analyzer.py .
	@$(PY_VENV) -m mypy --exclude '.venv,maze_analyzer.py' . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: all clean fclean re run install debug lint