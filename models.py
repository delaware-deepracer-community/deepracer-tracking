from deepracer import boto3_enhancer
import datetime
import concurrent.futures
from config import settings
from cwatch_logging import CWatch_logging as cwl
import traceback


class JPMCModels:
    """
    This class for interacting with all the models created and trained on the sandbox
    """

    def __init__(self):
        """
        This is costructor to initialize the HPMCModels object.
        """

        self.deepracer_client = boto3_enhancer.deepracer_client()
        self.all_models = []
        self.next_token = ''
        self.total_count = 0
        self.all_model_arns = {}
        self.models_by_duration = {}
        self.stopped_models = []
        self.imported_models = []
        self.cwlog = cwl()

    def get_model_and_count(self, NextToken=''):
        """
        This method is for fetching models and model count in each batch.
        """

        if NextToken == '':
            dr_models = self.deepracer_client.list_models(ModelType='REINFORCEMENT_LEARNING', MaxResults=100)
        else:
            dr_models = self.deepracer_client.list_models(ModelType='REINFORCEMENT_LEARNING', MaxResults=100, NextToken=NextToken)
        self.all_models = self.all_models + dr_models['Models']
        next_token = dr_models['NextToken'] if 'NextToken' in  dr_models else ''
        model_count = len(dr_models['Models'])
        return model_count, next_token

    def get_all_models(self):
        """
        This method is for fetching all models and total count in console.
        """

        while True:
            model_count, self.next_token = self.get_model_and_count(self.next_token)
            # print(model_count)
            self.total_count = self.total_count + model_count
            if model_count < 100:
                break
        # print(self.all_models[0])
        # print(self.total_count)
        self.cwlog.send_log(f"DR-Models: Model being stopped: {self.total_count}")

    def get_all_model_training_details(self, all_arns=[]) -> None:
        """
        This method is for fetching all model trainign details including the running ones.
        """

        while len(all_arns) > 0:
            arn = all_arns.pop()
            self.get_training_details(arn)

    def get_training_details(self, arn):
        """
        This method is for fetching details of a model.
        """
        try:
            training_details = self.deepracer_client.list_training_jobs(ModelArn=arn)
            creation_time = str(datetime.datetime.fromtimestamp(training_details['TrainingJobs'][0]['ActivityJob']['CreationTime']/1000)) \
                            if 'CreationTime' in training_details['TrainingJobs'][0]['ActivityJob'] else ''
            start_time = str(datetime.datetime.fromtimestamp(training_details['TrainingJobs'][0]['ActivityJob']['StartTime']/1000)) \
                            if 'StartTime' in training_details['TrainingJobs'][0]['ActivityJob'] else ''
            end_time = str(datetime.datetime.fromtimestamp(training_details['TrainingJobs'][0]['ActivityJob']['EndTime']/1000)) \
                            if 'EndTime' in training_details['TrainingJobs'][0]['ActivityJob'] else ''
            training_status = training_details['TrainingJobs'][0]['ActivityJob']['Status']['JobStatus'] \
                            if 'JobStatus' in training_details['TrainingJobs'][0]['ActivityJob']['Status'] else ''
            max_training_time = training_details['TrainingJobs'][0]['Config']['TerminationConditions']['MaxTimeInMinutes'] \
                            if 'MaxTimeInMinutes' in training_details['TrainingJobs'][0]['Config']['TerminationConditions'] else ''
            # updating the global variable for arns
            if self.all_model_arns != {}:
                self.all_model_arns[arn]['creation_time'] = creation_time
                self.all_model_arns[arn]['start_time'] = start_time
                self.all_model_arns[arn]['end_time'] = end_time
                self.all_model_arns[arn]['training_status'] = training_status
                self.all_model_arns[arn]['max_training_time'] = max_training_time
            else:
                return creation_time, start_time, training_status, max_training_time
        except Exception as ex:
            # print(ex)
            self.cwlog.send_log(f'DR-Models: Encountered exception: {ex}')
            self.cwlog.send_log(f'DR-Models: Exception Stacktrace: {traceback.extract_stack()}')
            return ()
    
    def get_all_model_training_details_concurrent(self) -> None:
        """
        This method is for fetching all model trainign details including the running ones using multiple threads.
        """

        # saving model arns to list
        all_arns = list(self.all_model_arns.keys())

        # multi-threaded fetch
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for i in range(1):
                executor.submit(self.get_all_model_training_details, all_arns)

    def get_all_model_arns(self) -> dict:
        """
        This method is for isolating arns and models names to a dictionary.
        """

        try:
            self.all_model_arns = {x['ModelArn']: {'ModelName': x['ModelName']} for x in self.all_models}
        except Exception as ex:
            # print(ex)
            self.cwlog.send_log(f'DR-Models: Encountered exception: {ex}')
            self.cwlog.send_log(f'DR-Models: Exception Stacktrace: {traceback.extract_stack()}')

    def delete_model(self, arn):
        """
        This method is to delete a model based on arn
        """
        try:
            print(self.deepracer_client.delete_model(ModelArn=arn))
            self.cwlog.send_log(f'DR-Models: Deleting Model: {arn}')
        except Exception as ex:
            # print(ex)
            self.cwlog.send_log(f'DR-Models: Encountered exception: {ex}')
            self.cwlog.send_log(f'DR-Models: Exception Stacktrace: {traceback.extract_stack()}')

    def stop_training_job(self, arn):
        """
        This method is for stopping a training job for model
        """

        try:
            self.deepracer_client.stop_training_reinforcement_learning_model(ModelArn=arn)
        except Exception as ex:
            # print(ex)
            self.cwlog.send_log(f'DR-Models: Encountered exception: {ex}')
            self.cwlog.send_log(f'DR-Models: Exception Stacktrace: {traceback.extract_stack()}')

    def filter_running_models_by_duration(self, duration):
        """
        This method is for filtering all the models crossing duration threshold which are running
        """
        
        try:
            for k, v in self.all_model_arns.items():
                if 'training_status' in v:
                    if v['training_status'] == 'IN_PROGRESS':
                        if 'max_training_time' in v:
                            if v['max_training_time'] > duration:
                                self.models_by_duration[k] = v
                                
            if self.models_by_duration != {}:
                for k, v in self.models_by_duration.items():
                    # print(f"Model being stopped: {v['ModelName']}")
                    self.cwlog.send_log(f"DR-Models: Model being stopped: {v['ModelName']}")
                    self.stop_training_job(k)
        except Exception as ex:
            # print(ex)
            self.cwlog.send_log(f'DR-Models: Encountered exception: {ex}')
            self.cwlog.send_log(f'DR-Models: Exception Stacktrace: {traceback.extract_stack()}')
    
    def stop_models_crossing_duration(self):
        """
        This mothod is to validate if model training has crossed threshold duration time and stop it
        """
        for arn, model in self.models_by_duration.items():
            now_time = datetime.datetime.now()
            start_time = datetime.datetime.strptime(model['start_time'])
            elapsed_time = now_time-start_time

            if elapsed_time > settings.DURATION_THRESHOLD:
                self.stop_training_job(arn)
                
    def filter_stopped_models(self):
        """
        This mothod is to filter the models that were stopped by automation.
        """
        
        for k, v in self.all_model_arns.items():
            if 'end_time' in v:
                if 'max_training_time' in v:
                    if v['max_training_time'] > settings.DURATION_THRESHOLD:
                        if v['training_status'] == 'COMPLETED':
                            start_time = datetime.datetime.strptime(v['start_time'].split('.')[0], '%Y-%m-%d %H:%M:%S')
                            end_time = datetime.datetime.strptime(v['end_time'].split('.')[0], '%Y-%m-%d %H:%M:%S')
                            run_time = end_time - start_time
                            
                            if settings.DURATION_THRESHOLD > int(run_time.total_seconds()/60):
                                self.stopped_models.append(k)
                                
    def filter_imported_models(self):
        """
        This mothod is to filter the models that were imported.
        """
        
        for k, v in self.all_model_arns.items():
            if 'end_time' in v:
                if v['end_time'] == '':
                    self.imported_models.append(k)

# jPMCModels = JPMCModels()
# jPMCModels.get_all_models()
# jPMCModels.get_all_model_arns()
# # print(jPMCModels.all_model_arns)

# jPMCModels.get_all_model_training_details_concurrent()
# print("Filtering")
# jPMCModels.filter_stopped_models()
# print(jPMCModels.stopped_models)
# jPMCModels.filter_imported_models()
# print(jPMCModels.imported_models)
# jPMCModels.filter_running_models_by_duration(settings.DURATION_THRESHOLD)
# # print(jPMCModels.all_model_arns)
# print(jPMCModels.models_by_duration if jPMCModels.models_by_duration != set() else False)

# creation_time, start_time, training_status, max_training_time = jPMCModels.get_training_details('arn:aws:deepracer:us-east-1:158809224514:model/reinforcement_learning/760d4f7f-435f-4187-9ebf-236633c1dc03')
# creation_time, start_time, training_status, max_training_time = jPMCModels.get_training_details('arn:aws:deepracer:us-east-1:158809224514:model/reinforcement_learning/12f3046e-cc8d-447c-a4d5-2040fc467ffd')
# print(f'Creation Time is: {creation_time}, Start time is: {start_time}, Training status is: {training_status}, Max Time is: {max_training_time}')

# jPMCModels.delete_model('arn:aws:deepracer:us-east-1:158809224514:model/reinforcement_learning/3a3cf3a3-ec76-4d44-84c9-e9adfa5412eb')

# jPMCModels.stop_training_job('arn:aws:deepracer:us-east-1:158809224514:model/reinforcement_learning/3a3cf3a3-ec76-4d44-84c9-e9adfa5412eb')