1. Install sanic - pip install sanic
2. You may need to install scoop if not installed (windows command line installer)
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser # Optional: Needed to run a remote script the first time
   irm get.scoop.sh | iex
3. Install migration tool - scoop install dbmate 
4. Install all requirements by - pip install -r requirements.txt
5. dbmate -u 'postgres://<db_user>:<db_pass>@localhost:<port>/<db_name>?sslmode=disable' up


Run app - sanic service:app --debug --reload

![Screenshot 2023-08-09 124201](https://github.com/TechLead-War/wallet/assets/53389091/39073c4b-4565-42ad-95ff-102f91cd2b39)


Table users {
  id integer [primary key]
  customer_xid string
  token string 
}

Table wallet {
  id integer [primary key]
  amount integer
  customer_xid string
  enabled_at timestamp
  is_enabled boolean
}

Table transactions {
  id integer [primary key]
  amount number
  final_amount number
  status string
  transaction_time timestamp
  transaction_from string
  transaction_to string
  transaction_type string
  reference_id string
}

Ref: users.customer_xid - wallet.customer_xid // many-to-one
Ref: users.customer_xid < transactions.transaction_from // many-to-one
Ref: users.customer_xid < transactions.transaction_to // many-to-one 


Note: This service is using tortoise-ORM for database interaction.
