#!/usr/bin/python
# -*- coding: UTF-8 -*

from utils.smtp_helper import notify_approvers
import traceback
from flask import request
from flask_restful import Resource
from utils.log_helper import lg
from utils.status_code import response_code
from common.common_model_enum import modelEnum
from common.common_response_process import response_result_process
from common.common_request_process import req
from db.gcp.task_operator import taskOperator
from common.common_login_helper import login_required
from core.dashboard_singleton import dashboard_singleton


class interfaceSystemNotify(Resource):


    @login_required
    def get(self,):
        xml = request.args.get('format')
        try:
            request_data = req.request_process(request, xml, modelEnum.department.value)
            if isinstance(request_data, bool):
                request_data = response_code.REQUEST_PARAM_FORMAT_ERROR
                return response_result_process(request_data, xml=xml)
            # if not request_data:
            #     data = response_code.REQUEST_PARAM_MISSED
            #     return response_result_process(data, xml=xml)
            try:
                user_key = req.get_user_key()
                account_id = req.get_user_key()
                workspace_id = req.get_workspace_id()
                # print('user id:', user_key)
                data = response_code.SUCCESS
                data['data'] = dashboard_singleton.get_notify(user_key)
            except:
                data = response_code.GET_DATA_FAIL
                data['msg'] = 'Token error or expired, please login again.'
            # # print(data)
            return response_result_process(data, xml=xml)
        except Exception as e:
            lg.error(e)
            # print(traceback.format_exc())
            error_data = response_code.GET_DATA_FAIL
            return response_result_process(error_data, xml=xml)


    def post(self,):
        xml = request.args.get('format')
        try:
            request_data = req.request_process(request, xml, modelEnum.department.value)
            if isinstance(request_data, bool):
                request_data = response_code.REQUEST_PARAM_FORMAT_ERROR
                return response_result_process(request_data, xml=xml)

            try:
                user_key = req.get_user_key()
                account_id = req.get_user_key()
                workspace_id = req.get_workspace_id()

            except:
                data = response_code.GET_DATA_FAIL
                data['msg'] = 'Token error or expired, please login again.'
                return response_result_process(data, xml=xml)
            # request_data = req.verify_all_param(request_data, governanceApiPara.changeStatus_POST_request)
            nodify_id = request_data.get('nodify_id', None)
            is_read = request_data.get('is_read', None)
            if not nodify_id:
                data = response_code.GET_DATA_FAIL
                data['msg'] = 'please pass a nodify id.'
                return data
            # # print('user id:', user_key)
            # change status
            data = dashboard_singleton.read_notify(user_key, nodify_id, is_read)

            return response_result_process(data, xml=xml)
        except Exception as e:
            lg.error(traceback.format_exc())
            error_data = response_code.GET_DATA_FAIL
            return response_result_process(error_data, xml=xml)