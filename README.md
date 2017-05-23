
The server will provide access to the OneTouchReveal API (actually a web scraper), and
the Fitbit API.

OneTouchReveal:
 - client device will store username and password
 - each request to this server will include username and password
 - user will be logged in, request will be completed, user will be logged out

Fitbit:
 - upon first request, client device will be redirected to Fitbit login page
 - server will store username, hashed Fitbit auth token, and Fitbit refresh token
 - client will make subsequent requests using username and Fitbit auth token
 - server will check authorization using the username and auth token, then complete the request
 - server will manage user login state and user refresh token if necessary
