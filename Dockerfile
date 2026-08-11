FROM python:3.10-slim-bookworm

WORKDIR /Jisshu-filter-bot

# Debian bookworm 'ਚ apt-get ਨਾਲ --fix-missing ਵਰਤੋ (ਵਧੇਰੇ ਸਥਿਰ)
RUN apt-get update -y --fix-missing && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x start.sh

CMD ["bash", "start.sh"]
