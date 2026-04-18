# Granit OS Image & Configuration

## Architecture

- **pi-gen**: builds a minimal Raspberry Pi OS Lite image (packages + boot config)
- **Ansible**: configures all services, security, and monitoring

This split means you can either:
1. Flash the custom image and it's ready to provision
2. Flash stock Raspberry Pi OS and run `make provision`

## Quick Start

```bash
# Option A: Build custom image
make build
# Flash to eMMC via rpiboot + rpi-imager

# Option B: Use stock Raspberry Pi OS Lite
# Flash via rpi-imager, boot, connect Ethernet

# Then provision via Ansible
make provision
```

## Configuration

After provisioning, edit `/etc/granit/sync.conf`:

```bash
SYNC_REMOTE=":sftp,host=100.x.x.x,user=backup,key_file=/home/granit/.ssh/id_ed25519:/backups"
WAKE_HOUR=04
METRICS_URL="http://192.168.1.x:8428/api/v1/import/prometheus"
```

Then enable the backup cycle:

```bash
sudo systemctl enable --now granit-cycle.timer
```

## Ansible Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `granit_timezone` | `UTC` | System timezone |
| `granit_wake_hour` | `04` | RTC wake hour (24h) |
| `granit_sync_remote` | `""` | rclone remote path |
| `granit_metrics_url` | `""` | Prometheus remote-write URL |

## Structure

```
software/
├── Makefile              # build image or provision
├── hardware-test.sh      # hardware validation script
├── pi-gen/               # image build (packages + boot config)
│   ├── config
│   └── stage-granit/
│       ├── 00-install-packages/
│       └── 01-config/
└── ansible/              # device configuration
    ├── playbook.yml
    ├── inventory/
    └── roles/granit/
        ├── tasks/main.yml
        ├── templates/
        └── files/
```
