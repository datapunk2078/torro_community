from api.gcp.tasks.baseTask import baseTask
from google.cloud import storage
class CreateGCSBucket(baseTask):
    api_type = 'gcp'
    api_name = 'CreateGCSBucket'
    arguments = {"porject_id": {"type": str, "default": ''},
                 "usecase_name": {"type": str, "default": ''},
                 "bucket_location": {"type": str, "default": ''},
                 "bucket_name": {"type": str, "default": ''},
                 "bucket_class ": {"type": str, "default": ''},
                 "bucket_cmek": {"type": str, "default": ''},
                 "bucket_labels": {"type": str, "default": ''}}

    def __init__(self, stage_dict):
        super(CreateGCSBucket, self).__init__(stage_dict)
        self.target_project = stage_dict['porject_id']

    def execute(self, workspace_id=None, form_id=None, input_form_id=None, user_id=None):
        missing_set = set()
        for key in self.arguments:
            if key == 'bucket_cmek' or key == 'bucket_class' or key == 'bucket_labels':
                continue
            check_key = self.stage_dict.get(key, 'NotFound')
            if check_key == 'NotFound':
                missing_set.add(key)
            # # print('{}: {}'.format(key, self.stage_dict[key]))
        if len(missing_set) != 0:
            return 'Missing parameters: {}'.format(', '.join(missing_set))
        else:
            project_id = self.stage_dict['porject_id'].strip()
            bucket_name = self.stage_dict['bucket_name'].strip()
            location = self.stage_dict['bucket_location'].strip()
            bucket_labels_str = self.stage_dict.get('bucket_labels', '').strip()
            bucket_labels = {}
            for bucket_label in bucket_labels_str.split(','):
                key, value = bucket_label.split('=')
                bucket_labels[key.strip()] = value.strip()

            bucket_class = self.stage_dict.get('bucket_class', None).strip()
            bucket_cmek = self.stage_dict.get('bucket_cmek', None).strip()
            storage_client = storage.Client(project_id)

            bucket = storage_client.create_bucket(bucket_name, location=location)
            if bucket_class:
                bucket.storage_class = bucket_class
            if bucket_labels:
                labels = bucket.labels
                for label in bucket_labels:
                    labels["label"] = bucket_labels[label]
                bucket.labels = labels
            # if bucket_cmek:
            #     bucket.default_kms_key_name = bucket_cmek
            bucket.patch()

            usecase_name = self.stage_dict.get('usecase_name', None)
            self.records_resource(workspace_id, input_form_id, usecase_name, 'Storage', bucket_name)

            return "Bucket {} created.".format(bucket.name)