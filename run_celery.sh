#!/bin/bash
sleep 10
celery -A img_finder worker -l INFO --uid=nobody --gid=nogroup