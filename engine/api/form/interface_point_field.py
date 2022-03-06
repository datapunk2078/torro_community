#!/usr/bin/python
# -*- coding: UTF-8 -*

from utils.api_version_verify import api_version
from flask import request
from flask_restful import Resource
from core.form_singleton import formSingleton_singleton
from utils.status_code import response_code
from common.common_model_enum import modelEnum
from common.common_response_process import response_result_process
from common.common_login_helper import login_required
from common.common_request_process import req
from db.form.db_form_parameter import formApiPara
import traceback
import logging

logger = logging.getLogger("main." + __name__)

class interfacePointField(Resource):

    # @api_version
    # @login_required
    # def get(self, ):
    #     xml = request.args.get('format')
    #     try:
    #         workspace_id = req.get_workspace_id()
    #         data = formSingleton_singleton.get_all_fields(workspace_id)
    #         body = modelEnum.form.value.get('body')
    #
    #         return response_result_process(data, xml_structure_str=body, xml=xml)
    #
    #     except Exception as e:
    #         logger.error("FN:interfaceFieldTemplate_get error:{}".format(traceback.format_exc()))
    #         error_data = response_code.GET_DATA_FAIL
    #         return response_result_process(error_data, xml=xml)
    # @api_version
    @login_required
    def post(self):
        xml = request.args.get('format')
        try:
            request_data = req.request_process(request, xml, modelEnum.department.value)
            if isinstance(request_data, bool):
                request_data = response_code.REQUEST_PARAM_FORMAT_ERROR
                return response_result_process(request_data, xml=xml)
            # if not request_data:
            #     data = response_code.REQUEST_PARAM_MISSED
            #     return response_result_process(data, xml=xml)

            # request_data = req.verify_all_param(request_data, formApiPara.getFieldTemplate_POST_request)
            workspace_id = req.get_workspace_id()
            field_info = request_data.get('data', {})
            field_type = request_data.get('field_type', None)
            if field_type is None:
                return response_code.GET_DATA_FAIL
            data = formSingleton_singleton.add_point_field(field_info, field_type, workspace_id)
            if data['code'] == 200:
                response_data = data['data']
                data['data'] = req.verify_all_param(response_data, formApiPara.getFieldTemplate_POST_response)

            return response_result_process(data, xml=xml)

        except Exception as e:
            logger.error("FN:interfacePointField_post error:{}".format(traceback.format_exc()))
            error_data = response_code.GET_DATA_FAIL
            return response_result_process(error_data, xml=xml)
