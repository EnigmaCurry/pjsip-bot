# Justfile

# Set a default shell for command grouping
set shell := ["bash", "-cu"]

# Create and activate a virtual environment
env:
	uv venv env
	echo "Run 'just activate' to enter the venv"

# Print instructions to activate the venv manually
activate:
	. env/bin/activate && bash -l

# Optional: install dependencies from pyproject.toml
install:
	uv pip install -r requirements.txt

# Optional: run your bot script inside the venv
run:
	. env/bin/activate && python main.py
