#!/bin/bash


cd /home/fischer/IT/projects/chess-rl/ || exit
uvicorn backend.api.main:app --reload