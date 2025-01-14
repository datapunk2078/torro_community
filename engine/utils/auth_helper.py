#!/usr/bin/python
# -*- coding: UTF-8 -*
"""
@author：li-boss
@file_name: auth_helper.py
@create date: 2019-10-27 14:17 
@blog https://leezhonglin.github.io
@csdn https://blog.csdn.net/qq_33196814
@file_description：
"""
import json
import sys

import datetime
import jwt
import time
from flask import abort
from common.common_crypto import prpcrypt
from common.common_hash_key import secret_key
from utils.smtp_helper import Smtp
from utils.ldap_helper import Ldap
import api
from db.user.db_user_mgr import user_mgr
from utils.status_code import response_code
import traceback

class Auth(object):
    """
    权限校验、token帮助类
    """
    # host = "23.101.10.96"
    # port = 636
    # ADMIN_DN = "admin@torro.ai"
    # ADMIN_PASSWORD = "LSr2go1gifBc5Nk6F+qM2A=="
    # ADMIN_PASSWORD = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsZGFwX3B3ZCI6IjQ3NDU1RGdkZWVAIn0.Xg-iseNmc7efidKM-THSrxC34-GuNq-e2JBp4i3W8vI"
    # SEARCH_BASE = "ou=AADDC Users,dc=torro,dc=ai"

    @staticmethod
    def ldap_auth(username, password):

        return Ldap.ldap_auth(username, password)

    @staticmethod
    def __encode_pwd(pwd):
        pwd = jwt.encode(
            pwd,
            api.Config.SECRET_KEY,
            algorithm='HS256'
        )
        return pwd

    @staticmethod
    def __decode_pwd(pwd):
        pwd = jwt.decode(pwd, api.Config.SECRET_KEY)
        return pwd

    def __encode_auth_token(self, user_key, account_id, permissions, role_list, role, workspace_list, workspace_id, login_time):
        """
        生成认证Token
        :param USER_KEY: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            ##exp: 过期时间
            ##nbf: 表示当前时间在nbf里的时间之前，则Token不被接受
            ##iss: token签发者
            ##aud: 接收者
            ##iat: 发行时间
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'data': {
                    'user_key': user_key,
                    'account_id': account_id,
                    'permissions': permissions,
                    'role_list': role_list,
                    'user_role': role,
                    'workspace_list': workspace_list,
                    'workspace_id': workspace_id,
                    'login_time': login_time
                }
            }
            # print ('pyaload', payload)
            return jwt.encode(
                payload,
                api.Config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def __decode_auth_token(self, auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            ###30分钟无访问token过期
            payload = jwt.decode(auth_token, api.Config.SECRET_KEY, leeway=datetime.timedelta(seconds=30))
            # # print("payload:", payload)
            # 取消过期时间验证
            # payload = jwt.decode(auth_token, api.Config.SECRET_KEY, options={'verify_exp': False})
            if ('data' in payload and 'user_key' in payload['data'] and 'permissions' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'
        except TypeError:
            return '无效Token'
        except:
            print(sys.exc_info()[1])

    @classmethod
    def get_offline_password(cls, username):
        try:
            user = user_mgr.get_user_by_name(username)
            user_base_data = user.get('data', None)
            mail_host = "smtp.gmail.com"  # 设置服务器

            mail_user = "torroai@gmail.com"  # 用户名
            mail_pass = ""  # 口令
            sender = 'torroai@gmail.com'

            if user_base_data:
                new_password = secret_key(username, 32)
                data = user_mgr.update_user_password(username, new_password)
                return_count = data.get('data', {'count': 0})['count']
                if return_count > 0:
                    smtp_obj = Smtp(mail_host, mail_user, mail_pass, sender)
                    smtp_obj.send_email('TorroAi Login Info', 'Your offline password is: {}'.format(new_password),
                                        mail_user,  [username], 'TorroAi')
                return True
            else:
                return False
        except:
            # print(traceback.format_exc())
            return False
    @classmethod
    def authenticate(cls, username, password, offline_flag):
        """
        用户登录，登录成功返回token，写将登录时间写入数据库；登录失败返回失败原因
        :param password:
        :return: json
        """
        password = prpcrypt.decrypt(password)
        if offline_flag == 1:
            ad_group_list, ldap_username = user_mgr.offline_login(username, password)
        else:
            ad_group_list, ldap_username = Auth.ldap_auth(username, password)
        print('ad_group_list, ldap_username:', ad_group_list, ldap_username)
        if ldap_username is not None:
            user = user_mgr.get_user_by_name(username, ldap_username, ad_group_list)
        else:
            user = user_mgr.get_user_by_name(username)
        user_base_data = user.get('data')
        print('user_base_data: ', user_base_data, user)
        # 判断是有这个用户
        if (user_base_data is None):
            return response_code.LOGIN_FAIL
        if user_base_data:
            # ldap:
            if username == 'TorroAdmin' and password == user_base_data['PASS_WORD']:
                data = response_code.SUCCESS
                data['msg'] = '[ORG_SETTING]'
                data['token'] = prpcrypt.encrypt('[SETTING]')
                return data
            # print('ad_group_list', ad_group_list)
            if not ad_group_list:
                return response_code.LOGIN_IS_FAIL
            user_data = user_mgr.get_user_permissions(user_base_data['ID'], ad_group_list)
            # # print('user_data', user_data)
            # # print('role_list', user_data['role_list'])
            # 登录时间
            login_time = int(time.time())
            # # print('user_data', user_data)
            # 生成token
            token = cls.__encode_auth_token(cls, user_data.get('ID'), user_data.get('ACCOUNT_ID'), user_data.get('permissions'),
                                            user_data['role_list'], user_data['user_role'],
                                            user_data['workspace_list'], user_data['workspace_id'],
                                            login_time)
            # print('token', token)
            user_data['ad_group_list'] = user_data['GROUP_LIST']
            user_data.pop('GROUP_LIST')
            user_data.pop('PASS_WORD')
            user_data.pop('permissions')
            dict_user = user_data
            dict_user['token'] = token.decode()
            return dict_user
        else:
            return response_code.LOGIN_IS_FAIL

    @staticmethod
    def __check_permission(user_role, permissions, request_id, api_endpoint, method):
        # # print('permissions:', permissions)
        api_permission = '{}-{}'.format(api_endpoint, method)
        all_method_permission = '*-{}'.format(method)
        all_endpoint_permission = '{}-*'.format(api_endpoint)
        all_permission = '*-*'
        permission_allow = 0
        print('user_role:', user_role)
        print('permissions:', permissions)
        for id in permissions:
            if (request_id is None or id == request_id) and user_role in permissions[id]:
                if all_permission in permissions[id][user_role] or api_permission in \
                        permissions[id][user_role] or all_method_permission in \
                        permissions[id][user_role] or all_endpoint_permission in \
                        permissions[id][user_role]:
                    permission_allow = 1
                    break
        return permission_allow
    @classmethod
    def refresh_token(cls, request, role_name, workspace_id, new_workspace_id_dict=None, remove_workspace_id_dict=None):
        login_time = int(time.time())
        auth_token = request.cookies.get('token')
        # # print('auth_token', auth_token)
        payload = cls.__decode_auth_token(cls, auth_token)
        # print('payload:', payload)
        role_list = payload['data']['role_list']
        workspace_item_list = payload['data']['workspace_list']
        if new_workspace_id_dict:
            workspace_item_list.append(new_workspace_id_dict)
        workspace_list = []
        remove_workspace_index_list = []
        remove_workspace_list = []
        if remove_workspace_id_dict:
            for workspace in remove_workspace_id_dict:
                remove_workspace_list.append(workspace['value'])
        for index, workspace in enumerate(workspace_item_list):
            if workspace['value'] not in remove_workspace_list:
                workspace_list.append(workspace['value'])
            else:
                remove_workspace_index_list.append(index)
        for i in range(len(remove_workspace_index_list) - 1, -1, -1):
            workspace_item_list.pop(remove_workspace_index_list[i])

        # print(role_name, role_list)
        # print(workspace_id, workspace_list)
        if role_name is None or role_name not in role_list:
            role_name = payload['data']['user_role']
        if workspace_id is None or workspace_id not in workspace_list:
            workspace_id = workspace_list[0]
        # print(role_name, role_list)
        # print(workspace_id, workspace_list)
        token = cls.__encode_auth_token(cls, payload['data']['user_key'], payload['data']['account_id'], payload['data']['permissions'],
                                        role_list, role_name,
                                        workspace_item_list, workspace_id, login_time)
        # print('token:', token)
        return token.decode(), role_name, role_list, workspace_id, workspace_list


    @classmethod
    def identify(cls, request):
        """
        用户鉴权
        :return: list
        """
        auth_token = request.cookies.get('token')
        print('auth_token:', auth_token)
        if (auth_token):
            # Bearer cjidsfjsfi
            # workspace_id = request.cookies.get('workspace_id', '1')
            # usecase_id = request.cookies.get('usecase_id', '1')
            # team_id = request.cookies.get('team_id', '1')
            if not auth_token:
                data = response_code.TOKEN_ERROR
                data['msg'] = 'Your login status has expired. Please login again'
                return data, None, None
            else:
                payload = cls.__decode_auth_token(cls, auth_token)
                print('payload:', payload)
                if not isinstance(payload, str):
                    user_id = payload['data']['user_key']
                    account_id = payload['data']['account_id']
                    workspace_id = payload['data']['workspace_id']
                    user_role = payload['data']['user_role']
                    # team_permissions = payload['data']['permissions']['team']
                    usecase_permissions = payload['data']['permissions']['usecase']
                    workspace_permissions = payload['data']['permissions']['workspace']
                    org_permissions = payload['data']['permissions']['org']
                    # check if user exist
                    userInfo = user_mgr.get_user_by_id(user_id)

                    api_endpoint = request.endpoint
                    method = request.method
                    # # print('payload: ', payload)
                    if (userInfo is None):
                        abort(401, 'user not found')
                    else:
                        # print('org permission:')
                        permission_allow = Auth.__check_permission(user_role, org_permissions, None, api_endpoint, method)
                        if permission_allow == 0:
                            # print('workspace permission:')
                            permission_allow = Auth.__check_permission(user_role, workspace_permissions, workspace_id, api_endpoint, method)
                        # if permission_allow == 0:
                        #     # print('usecase permission:')
                        #     permission_allow = Auth.__check_permission(user_role, usecase_permissions, usecase_id, api_endpoint, method)
                        # if permission_allow == 0:
                        #     # print('team permission:')
                        #     permission_allow = Auth.__check_permission(user_role, team_permissions, team_id, api_endpoint, method)
                        if permission_allow == 1:
                            return user_id, account_id, workspace_id
                        else:
                            data = response_code.TOKEN_ERROR
                            data['msg'] = 'Your login status has expired. Please login again'
                            return data, None, None
                else:
                    data = response_code.TOKEN_ERROR
                    data['msg'] = 'Your login status has expired. Please login again'
                    return data, None, None
        else:
            data = response_code.TOKEN_ERROR
            data['msg'] = 'Your login status has expired. Please login again'
            return data, None, None