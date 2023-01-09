set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

SSH_SERVER := "linode"
POETRY_BIN := "~/.local/bin/poetry"  # TODO: Get this programmatically

alias rr := run-remote
run-remote file +args:
    scp {{file}} {{SSH_SERVER}}:/tmp/scan_cleanup.input.pdf
    ssh {{SSH_SERVER}} "cd ~/fast-scan-cleanup && {{POETRY_BIN}} run python fast-scan-cleanup.py -i /tmp/scan_cleanup.input.pdf -o /tmp/scan_cleanup.output.pdf {{args}}"
    scp {{SSH_SERVER}}:/tmp/scan_cleanup.output.pdf {{without_extension(file)}}.clean.pdf
