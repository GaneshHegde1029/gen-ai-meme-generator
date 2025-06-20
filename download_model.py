from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="stabilityai/sd-turbo",
    local_dir="./models/sd-turbo",
    local_dir_use_symlinks=False
)
