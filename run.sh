#!/bin/bash

FASTAPI_PORT=8000
STREAMLIT_PORT=8501

echo "Szukam procesów na portach $FASTAPI_PORT i $STREAMLIT_PORT..."

PID_FASTAPI=$(lsof -ti tcp:$FASTAPI_PORT)
PID_STREAMLIT=$(lsof -ti tcp:$STREAMLIT_PORT)

if [ -n "$PID_FASTAPI" ]; then
  kill -9 $PID_FASTAPI
fi

if [ -n "$PID_STREAMLIT" ]; then
  kill -9 $PID_STREAMLIT
fi


echo "Uruchamiam FastAPI na porcie $FASTAPI_PORT..."
nohup python -m uvicorn api_server:app --host 0.0.0.0 --port $FASTAPI_PORT --reload > api.log 2>&1 &

sleep 2

echo "Uruchamiam Streamlit na porcie $STREAMLIT_PORT..."
nohup streamlit run app.py --server.port $STREAMLIT_PORT > streamlit.log 2>&1 &

sleep 3

echo "Otwieram aplikację w przeglądarce..."
open "http://localhost:$STREAMLIT_PORT"

echo "System uruchomiony. API → :$FASTAPI_PORT | UI → :$STREAMLIT_PORT"
