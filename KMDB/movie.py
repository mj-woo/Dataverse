import json
import urllib
from urllib import request
import requests

base_url = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2"
serviceKey = "3N82P1IP3R8PM5O73YMK"

# GET request
def get_request():
    url = base_url
    # headers = {"ServiceKey": serviceKey}
    response = request.urlopen(request.Request(url))
    assert response.getcode() == 200
    json_data = response.read()
    json_pretty = json.loads(json_data.decode('utf-8'))
    print("JSON request body: ", json_pretty)
    return json_pretty

get_request()

# from django.views.decorators.csrf import csrf_exempt
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response


# @csrf_exempt
# @api_view(['GET'])
# def movie_list(request):
#     url = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&ServiceKey=3N82P1IP3R8PM5O73YMK"

#     request = urllib.request.Request(url)
#     response = urllib.request.urlopen(request)

#     rescode = response.getcode()

#     if rescode == 200:
#         response_body = response.read()
#         dict = json.loads(response_body.decode('utf-8'))
#         return Response(dict, status=status.HTTP_200_OK)
#     else:
#         return Response(rescode, status=status.HTTP_400_BAD_REQUEST)