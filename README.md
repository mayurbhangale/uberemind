WIP



How To Use This
---------------

1. Navigate over to https://developer.uber.com/, and sign up for an Uber developer account.
2. Register a new Uber application and make your Redirect URI `http://localhost:7000/submit` - ensure that both the `profile` and `history` OAuth scopes are checked.
3. Fill in the relevant information in the `config.json` file in the root folder and add your client id and secret as the environment variables `UBER_CLIENT_ID` and `UBER_CLIENT_SECRET`.
4. Run `export UBER_CLIENT_ID="`*{your client id}*`"&&export UBER_CLIENT_SECRET="`*{your client secret}*`"`
5. Run `pip install -r requirements.txt` to install dependencies
6. Run `python app.py`
7. Navigate to http://localhost:7000 in your browser

Deploy to Heroku
----------------

Click the button below to set up this sample app on Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

After creating your app on Heroku, you have to configure the redirect URL for your Uber OAuth app. Use a `https://`*{your-app-name}*`.herokuapp.com/submit` URL.
You will also want to configure the heroku environment variable FLASK_DEBUG=False in order to properly serve SSL traffic.
Development
-----------

If you want to work on this application I’d love your pull requests and tickets on GitHub!

1. If you open up a ticket, please make sure it describes the problem or feature request fully.
2. If you send us a pull request, make sure you add a test for what you added, and make sure the full test suite runs with `make test`.
