import datetime
import time

def schedule_runner(scheduled_datetime, run_script, global_config):
    # Check if a schedule was set; if not, exit the function.
    if scheduled_datetime is None:
        print("No schedule set; schedule runner exiting.")
        return

    now = datetime.datetime.now()
    wait_time = (scheduled_datetime - now).total_seconds()
    if wait_time > 0:
        print(f"Scheduled run in {wait_time:.2f} seconds.")
        time.sleep(wait_time)
    print("Scheduled time reached. Running script.")
    run_script()
    # Optionally, clear the schedule from the configuration after running:
    global_config.pop("schedule", None)