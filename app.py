import requests
import sys
import time
import os


_MAX_SECONDS_ALLOWED_FOR_TESTS = 600


def main():
    trigger_url = sys.argv[1]
    trigger_resp = requests.get(trigger_url)

    if trigger_resp.ok:
        trigger_json = trigger_resp.json().get("data", {})

        test_runs = trigger_json.get("runs", [])

        print("Started {} test runs.".format(len(test_runs)))

        results = {}
        deadline = time.time() + _MAX_SECONDS_ALLOWED_FOR_TESTS
        while len(results) < len(test_runs):
            if time.time() >= deadline:
                print('Some test runs did not complete in the allowed window of %s seconds'
                      % _MAX_SECONDS_ALLOWED_FOR_TESTS)
                exit(1)

            time.sleep(1)

            for run in test_runs:
                test_run_id = run.get("test_run_id")
                if test_run_id not in results:
                    result_data = _get_result(run)
                    if not result_data:
                        continue
                    result = result_data.get("result")
                    if result in ["pass", "fail"]:
                        results[test_run_id] = result_data
                    elif result == "working":
                        # Results aren't ready yet. Will retry the next
                        # time through the loop.
                        pass
                    else:
                        print("Got response with unknown result field. Full response was %s" % result_data)

        pass_count = sum([r.get("result") == "pass" for r in list(results.values())])
        fail_count = sum([r.get("result") == "fail" for r in list(results.values())])

        if fail_count > 0:
            print("{} test runs passed. {} test runs failed.".format(pass_count, fail_count))
            exit(1)

        print("All test runs passed.")


def _get_result(test_run):
    # generate Personal Access Token at https://www.runscope.com/applications
    if "RUNSCOPE_ACCESS_TOKEN" not in os.environ:
        print("Please set the environment variable RUNSCOPE_ACCESS_TOKEN. You can get an access token by going to https://www.runscope.com/applications")
        exit(1)

    API_TOKEN = os.environ["RUNSCOPE_ACCESS_TOKEN"]
    
    opts = {
        "base_url": "https://api.runscope.com",
        "bucket_key": test_run.get("bucket_key"),
        "test_id": test_run.get("test_id"),
        "test_run_id": test_run.get("test_run_id")
    }
    result_url = "{base_url}/buckets/{bucket_key}/tests/{test_id}/results/{test_run_id}".format(**opts)
    print("Getting result: {}".format(result_url))

    headers = {
        "Authorization": "Bearer {}".format(API_TOKEN),
        "User-Agent": "python-trigger-sample"
    }
    result_resp = requests.get(result_url, headers=headers)
    if result_resp.status_code == 404:
        print('Unable to find test run result at %s' % result_url)
        return
    if result_resp.ok:
        data = result_resp.json().get("data")
        if not data:
            print("Response data was empty. Full response was %s" % result_resp.text)
        return data

    # States Title, recently experenced a false positive. This should provide some
    # more information in the event of another failure
    print(
        "Result response not ok... Check Runscope for more information: "
        "https://www.runscope.com/radar/{bucket_key}/{test_id}/history/{test_run_id}"
        .format(**opts)
    )
    print("\n\nResponse: {}".format(result_resp.text))
    # Currently unrecoverable, TODO: revisit if false positive presist
    exit(1)


if __name__ == '__main__':
    main()
