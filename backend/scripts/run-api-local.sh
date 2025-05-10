#!/bin/bash


cd /path/to/chess-rl || exit
uvicorn backend.api.main:app --reload
