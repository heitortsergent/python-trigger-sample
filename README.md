# python-trigger-sample
Sample Python script for initiating test runs and checking for the results. Use this script in your CI process to start test runs and change the build status based on the result of the tests. If any of the triggered tests fail, the script will exit with a non-zero error code.

## Usage

 - Install requirements (virtualenv recommended): `pip install -r requirements.txt`
 - Set the environment variable `RUNSCOPE_ACCESS_TOKEN` in your CI provider
 - Run with a Trigger URL as the sole parameter: `python app.py https://api.runscope.com/radar/:uuid/trigger`

## Generating an API key

 - Create an application at https://www.runscope.com/applications
 - Use dummy URLs for the app and callback URL values (e.g. http://example.com)
 - Copy the Personal Access Token from the created app and update the script with that value
