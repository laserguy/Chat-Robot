FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install openai
# RUN pip install spacy
RUN python -m spacy download en_core_web_sm


COPY . .

CMD ["python", "-u", "endpoint.py"]