@echo off
pythonw.exe download_reviews.py %*
REM python.exe describe_reviews.py %1 723090
REM python.exe cluster_reviews.py %1 723090
python.exe identify_joke_reviews.py %1 723090
python.exe estimate_hype.py %*
