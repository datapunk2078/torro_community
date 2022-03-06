from api.gcp.tasks.baseTask import baseTask
from google.cloud import bigquery
class CreateBQDataset(baseTask):
    api_type = 'gcp'
    api_name = 'CreateBQDataset'
    arguments = {"porject_id": {"type": str, "default": ''},
                 "dataset_location": {"type": str, "default": ''},
                 "dataset_name": {"type": str, "default": ''},
                 # "dataset_class ": {"type": str, "default": ''},
                 "dataset_cmek": {"type": str, "default": ''},
                 "dataset_labels": {"type": str, "default": ''}}

    def __init__(self, stage_dict):
        super(CreateBQDataset, self).__init__(stage_dict)
        self.target_project = stage_dict['porject_id']

    def execute(self, workspace_id=None, form_id=None, input_form_id=None, user_id=None):
        missing_set = set()
        for key in self.arguments:
            if key == 'dataset_cmek' or key == 'dataset_labels':
                continue
            check_key = self.stage_dict.get(key, 'NotFound')
            if check_key == 'NotFound':
                missing_set.add(key)
            # # print('{}: {}'.format(key, self.stage_dict[key]))
        if len(missing_set) != 0:
            return 'Missing parameters: {}'.format(', '.join(missing_set))
        else:
            project_id = self.stage_dict['porject_id']
            dataset_name = self.stage_dict['dataset_name']
            location = self.stage_dict['dataset_location']
            dataset_labels_str = self.stage_dict.get('dataset_labels', '')
            dataset_labels = {}
            for dataset_label in dataset_labels_str.split(','):
                key, value = dataset_label.split('=')
                dataset_labels[key.strip()] = value.strip()

            dataset_cmek = self.stage_dict.get('dataset_cmek', None)
            # dataset = client.create_dataset(dataset, timeout=30)
            # storage_client = storage.Client(project_id)
            print('self.stage_dict:', self.stage_dict)
            bq_client = bigquery.Client(project=project_id)
            dataset_id = "{}.{}".format(project_id, dataset_name)
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = location
            # dataset.labels = dataset_labels
            # if dataset_class:
            #     dataset.storage_class = dataset_class
            if dataset_labels:
                dataset.labels = dataset_labels
            if dataset_cmek:
                dataset_param = dataset.to_api_repr()
                dataset_param['defaultEncryptionConfiguration'] = bigquery.EncryptionConfiguration(
                    dataset_cmek).to_api_repr()
                dataset = dataset.from_api_repr(dataset_param)
            bq_client.create_dataset(dataset)

            return print("Created dataset {}.{}".format(bq_client.project, dataset.dataset_id))