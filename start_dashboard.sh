#!/usr/bin/env bash

APP_DIR="/home/shersamsam/dashboard"
URL="http://localhost:8501"

cd "$APP_DIR" || exit 1

if ! curl -s -o /dev/null "http://localhost:8501/_stcore/health"; then
    nohup "$APP_DIR/.venv/bin/streamlit" run app.py \
        --server.headless true --server.port 8501 \
        >/tmp/streamlit_dashboard.log 2>&1 &
    for i in $(seq 1 30); do
        sleep 1
        if curl -s -o /dev/null "http://localhost:8501/_stcore/health"; then
            break
        fi
    done
fi

xdg-open "$URL" >/dev/null 2>&1
