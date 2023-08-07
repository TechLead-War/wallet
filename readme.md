1. Install flask - pip install sanic
2. You may need to install scoop if not installed (windows command line installer)
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser # Optional: Needed to run a remote script the first time
   irm get.scoop.sh | iex
3. Install migration tool - scoop install dbmate 
4. Install all requirements by - pip install -r requirements.txt
5. dbmate -u 'postgres://<db_user>:<db_pass>@localhost:<port>/<db_name>?sslmode=disable' up


Run app - sanic service:app --debug --reload


Note: This service is using tortoise-ORM for database interaction.
