# Justfile

# Set a default shell for command grouping
set shell := ["bash", "-cu"]

# Print help for available recipes
help:
	@just --list

# Create the virtual environment
env:
    if [ ! -d .venv ]; then uv venv; fi

clean:
    rm -rf deps .venv

# Activate the virtual env shell
activate: env
	uv run bash -l

# Install dependencies from pyproject.toml
install: env
	uv pip install

# Run the program in the virtual environment
run: env
	if [ ! -f .env ]; then cp .env-dist .env; fi && \
	LD_LIBRARY_PATH=/usr/local/lib env $(cat .env | xargs) uv run python main.py

deps: env
	sudo sh -c '\
		set -e && \
		os_id=$(. /etc/os-release && echo $ID) && \
		case "$os_id" in \
		  fedora|rhel|centos|rocky|almalinux) \
		    echo "✅ Installing build dependencies for $os_id..." && \
		    dnf install -y --skip-unavailable \
		      gcc \
		      make \
		      alsa-lib-devel \
		      openssl-devel \
		      libv4l-devel \
		      SDL2-devel \
		      SDL2_gfx-devel \
		      SDL2_image-devel \
		      SDL2_mixer-devel \
		      SDL2_net-devel \
		      SDL2_ttf-devel \
		      x264-devel \
		      ffmpeg-devel \
		      opus-devel \
		      opencore-amr-devel \
		      vo-amrwbenc-devel \
		      python3-devel \
		      libuuid-devel \
		      swig \
		    ;; \
		  *) \
		    echo "❌ Unsupported OS: $os_id. This recipe only supports Fedora-like systems." && \
		    exit 1 ;; \
		esac'

build: deps
    mkdir -p deps
    cd deps && \
    if [ ! -d pjproject ]; then \
      git clone https://github.com/enigmacurry/pjproject.git; \
    fi && \
    cd pjproject && \
    git fetch --all --tags && \
    git checkout 2.15.1 && \
    ./configure --enable-shared --with-python && \
    make dep && \
    make && \
    sudo make install && \
    cd pjsip-apps/src/swig/python && \
    uv run make && \
    uv run make wheel && \
    uv pip install dist/pjsua2-*.whl

python *args:
	LD_LIBRARY_PATH=/usr/local/lib uv run python {{args}}
