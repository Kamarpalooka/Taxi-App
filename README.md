## CONFIGURATIONS

### `DEVELOPMENT`
CORS_ORIGIN_ALLOW_ALL : Set To True:



### `PRODUCTION / STAGING`
CORS_ORIGIN_ALLOW_ALL : set to False:

CORS_ORIGIN_WHITELIST = (
    'http://',
)
: set all allowed host in the list



Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.


**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

