# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template
from models import JPMCModels
from config import settings
from apscheduler.schedulers.background import BackgroundScheduler
import google_ddns


# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

sandbox_model_arns = {}
def get_dr_report():
	jPMCModels = JPMCModels()
	jPMCModels.get_all_models()
	jPMCModels.get_all_model_arns()
	# print(jPMCModels.all_model_arns)

	jPMCModels.get_all_model_training_details_concurrent()
	print("Done fetch")
	jPMCModels.filter_running_models_by_duration(settings.DURATION_THRESHOLD)
	global sandbox_model_arns
	sandbox_model_arns['complete_list'] = jPMCModels.all_model_arns
	jPMCModels.filter_imported_models()
	jPMCModels.filter_stopped_models()
	sandbox_model_arns['imported_models'] = jPMCModels.imported_models
	sandbox_model_arns['stopped_models'] = jPMCModels.stopped_models

# running the report as background process
get_dr_report()
schedule = BackgroundScheduler(daemon=False)
schedule.add_job(get_dr_report, 'interval', seconds=900)
schedule.start()

# setting up schedule to update google ddns
google_ddns.update_ddns()
ddns_schedule = BackgroundScheduler(daemon=False)
ddns_schedule.add_job(google_ddns.update_ddns, 'interval', seconds=300)
ddns_schedule.start()

@app.route('/')
def hello_world():
	return 'Hello World'

@app.route("/report")
def get_report():
	global sandbox_model_arns
	# print(sandbox_model_arns)
	return render_template('report.html', result=sandbox_model_arns, title=settings.GOOGLE_DDNS.split('.')[0])

# main driver function
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8888)
