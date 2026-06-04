source .venv/bin/activate
export GRADIO_SERVER_NAME=0.0.0.0
export GRADIO_SERVER_PORT=7860
echo "URL - http://`hostname`.local:${GRADIO_SERVER_PORT}"
python app.py

