# Key-Logger (In-app Demo)

This is a **consent-based** desktop demo that records **keyboard and mouse events only while its own window is focused**.

It **does not**:
- install global keyboard/mouse hooks
- capture input from other applications
- monitor clipboard

## Run

```bash
python main.py
```

## Usage

- Click inside the window to focus it
- Press **Start**
- Type / click / scroll inside the window
- Press **Stop** to save a session file in `storage/`

## Safety / Ethics

This repo is intentionally scoped to **in-app event logging** for learning GUI event handling and input telemetry in your own application.

