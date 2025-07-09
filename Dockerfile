FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    bash bc procps net-tools iproute2 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r python_analytics/requirements.txt

RUN chmod +x monitor.sh

EXPOSE 8501

CMD bash -c "streamlit run python_analytics/dashboard.py & while true; do ./monitor.sh; sleep 300; done"
