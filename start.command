#!/bin/bash
cd "$(dirname "$0")"
python3 main.py || python main.py
open "llm-price.html"
