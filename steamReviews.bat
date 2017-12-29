@echo off
pythonw.exe download_reviews.py %*
python.exe cluster_reviews.py %1 723090
