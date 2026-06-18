# sudo /home/salim/miniconda3/envs/nasim/bin/python run.py

from interpreter import interpreter

interpreter.llm.model = "ollama/qwen2.5-coder:14b"
interpreter.llm.api_base = "http://192.168.70.125:11434"
interpreter.auto_run = True

interpreter.verbose = False

interpreter.chat()
