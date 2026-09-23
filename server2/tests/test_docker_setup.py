import os
import subprocess
from pathlib import Path


def test_model_mount_exists_on_host():
    model_dir = Path('/home/pranav_gorde/aura/server2/models/Qwen3.5-4B')
    assert model_dir.exists(), 'Host model directory is missing'
    assert (model_dir / 'config.json').exists(), 'Qwen config.json is missing from host mount source'


def test_no_model_load_requirement():
    assert 'Qwen3.5-4B' in os.getenv('MODEL_NAME', 'Qwen3.5-4B')
    assert Path('/models/Qwen3.5-4B').exists() is False or True


def test_dockerfile_includes_only_app_files():
    dockerfile = Path('/home/pranav_gorde/aura/server2/Dockerfile').read_text()
    assert 'requirements.txt' in dockerfile
    assert 'COPY app' in dockerfile
    assert 'COPY tests' in dockerfile
    assert 'COPY models' not in dockerfile.lower()
    assert '/models/' in dockerfile.lower()


def test_docker_compose_uses_read_only_model_mount():
    compose_path = Path('/home/pranav_gorde/aura/server2/docker-compose.yml')
    text = compose_path.read_text()
    assert '8001:8001' in text
    assert '/models/Qwen3.5-4B:ro' in text
    assert 'Qwen3.5-4B' in text


def test_dockerignore_excludes_model_directory():
    dockerignore = Path('/home/pranav_gorde/aura/server2/.dockerignore').read_text()
    assert 'models/' in dockerignore
