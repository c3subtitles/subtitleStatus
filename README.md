subtitleStatus
==============

Setting up a minimal local testing environment:
```
mkvirtualenv subtitlesStatus -p $(which python3)
pip install -r requirements.txt
./init_test_database.sh
python manage.py runserver
```