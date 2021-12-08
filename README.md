Ref [https://testdriven.io/courses/taxi-react/](http://localhost:3000) site.<br>
Ref [https://github.com/testdrivenio/taxi-react-app/tree/master/server/taxi](http://localhost:3000) site.<br>
Ref [https://coursehunters.online/c/podelitsya-kursom-knigoj-i-td](http://localhost:3000) site.
Ref [http://localhost:3000](http://localhost:3000) React.

## CONFIGURATIONS

### `DEVELOPMENT`
CORS_ORIGIN_ALLOW_ALL : Set To True:



### `PRODUCTION / STAGING`
CORS_ORIGIN_ALLOW_ALL : set to False:

CORS_ORIGIN_WHITELIST = (
    'http://',
)
: set all allowed host in the list


**Note: this is a one-way operation. Once you `eject`, you can’t go back!**


# ENVIRONMENT VARIABLES
# NB: [Make sure to combine all env varsin .env to dev.env. Then use "os.getenv(par1, par2)]
Local ENV uses = [.env]
**comment [# "HOST": config("SQL_HOST", "localhost")] in the database configuration in the settings file
**uncomment [# "HOST": config("SQL_HOST", "localhost")] in the database configuration in the settings file
Docker ENV uses  = [dev.env]
**uncomment [# "HOST": config("SQL_HOST", "localhost")] in the database configuration in the settings file
**comment[# "HOST": config("SQL_HOST", "localhost")] in the database configuration in the settings file

