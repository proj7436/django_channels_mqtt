from django.shortcuts import render, redirect
from django.conf import settings
from .mqtt_utils import client as mqtt_client
from django.contrib.auth import authenticate
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.cache import cache
from django.views import View



USERNAME =  'admin_acc'
PASSWORD =  'admin365!@'
def publish_message(request):
    request_data = json.loads(request.body)
    rc, mid = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return JsonResponse({'code': rc})



def index(request):
    is_login = request.session.get('is_login', False)
    if is_login:
        return render(request, 'index.html')

    return redirect('login')


class login(View):
    global USERNAME, PASSWORD
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Đăng nhập người dùng
            request.session['is_login'] = True
            return redirect('index')
        else:
            request.session['is_login'] = False
            
            # Xử lý trường hợp đăng nhập không thành công
            return render(request, 'login.html', {'error_message': 'Login failed!'})
def get_all_topics(request):

    list_all_topics = cache.get('all_topics', [])

    if not list_all_topics:
        cache.set('all_topics', [], settings.CACHE_TIMEOUT)

    return JsonResponse({
        'all_topics':cache.get('all_topics')   
    })

def run_python_program(topic, qos, hex_str):
    new_hex_str = ''
    # global new_hex_str
    result_dict = {
        "Topic": topic,
        "QoS": qos,
        "Hex_Str": hex_str
    }

    def process_block_type2(part_header, new_hex_str):
        result = []
        result.append(f'{part_header}: {new_hex_str}')
        return result

    def display_cmd(hex_value, cmd_mapping):
        if hex_value in cmd_mapping:
            cmd_name = cmd_mapping[hex_value]
            return f"Device ({cmd_name}): {hex_value}"
        else:
            return f"Unknown cmd: {hex_value}"

    cmd_mapping = {
        "0a": "SET_ACK",
        "0b": "CONFIRM_SET_ACK_RECEIVED",
        "0c": "GET",
        "0d": "NOTIFY_MSG",
        "0e": "NOTIFY_SUCCESS",
        "0f": "NOTIFY_ERROR",
        "10": "APP_SUPPORT",
        "09": "SET_UNACK"
    }

    hex_str = hex_str.replace(" ", "")
    hex_value_1st_digit = hex_str[0:2]
    cmd_result = display_cmd(hex_value_1st_digit, cmd_mapping)

    header_result = []
    header_result.append("\nDEVICE STATUS\n\n")
    header_result.append(f"{cmd_result}")

    # Pair 2: msg_cmd_section
    header_result.extend(process_block_type2("Msg_Cmd_Section", hex_str[2:4]))

    # Pair 3: DEVICE STATUS
    header_result.append("\n\nSectionExtras")
    header_result.extend(process_block_type2("DEVICE STATUS", hex_str[4:6]))

    # Pair 4: msg_cmd_section_extra
    header_result.extend(process_block_type2("msg_cmd_section_extra", hex_str[6:8]))

    # Pair 5: Note
    header_result.append("\nMsgData")
    header_result.extend(process_block_type2("None", hex_str[8:10]))

    # Pair 6 + 7: TCP_UDP Port
    header_result.extend(process_block_type2("TCP_UDP Port", hex_str[10:14]))

    # Pair 8 + 9: Tid
    header_result.extend(process_block_type2("Tid", hex_str[14:18]))

    # Pair 10: sender_from
    header_result.extend(process_block_type2("sender_from", hex_str[18:20]))

    # Pair 11: sender_size
    header_result.extend(process_block_type2("sender_size", hex_str[20:22]))

    # Pair after Pair 11: sender_bytes_as sender_size
    sender_size_decimal = int(''.join(filter(str.isalpha, hex_str[20:22])), 16)
    header_result.extend(process_block_type2("sender_bytes_as sender_size", hex_str[22:22 + sender_size_decimal*2]))

    # KẾT THÚC PHẦN HEADER
    header_result.append("\n\nBlock")
    header_result.extend(process_block_type2("\nblockVersion (Firmware version)", hex_str[22 + sender_size_decimal*2: 24 + sender_size_decimal*2]))
    header_result.extend(process_block_type2("\tLength", hex_str[24 + sender_size_decimal*2: 26 + sender_size_decimal*2]))
    block_size_decimal1 = int(hex_str[24 + sender_size_decimal*2: 26 + sender_size_decimal*2], 16)
    header_result.extend(process_block_type2("\tData", hex_str[26 + sender_size_decimal*2: 26 + sender_size_decimal*2 + 2*block_size_decimal1]))
    
    header_result.extend(process_block_type2("\nblockDataLong (Up time)", hex_str[26 + sender_size_decimal*2 + 2*block_size_decimal1:28 + sender_size_decimal*2 + 2*block_size_decimal1]))
    header_result.extend(process_block_type2("\tLength", hex_str[28 + sender_size_decimal*2 + 2*block_size_decimal1:30 + sender_size_decimal*2 + 2*block_size_decimal1]))
    block_size_decimal2 = int(hex_str[28 + sender_size_decimal*2 + 2*block_size_decimal1:30 + sender_size_decimal*2 + 2*block_size_decimal1], 16)
    header_result.extend(process_block_type2("\tData", hex_str[30 + sender_size_decimal*2 + 2*block_size_decimal1:30 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2]))

    header_result.extend(process_block_type2("\nblockDataLong (Last time activate)", hex_str[30 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2:32 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2]))
    header_result.extend(process_block_type2("\tLength", hex_str[32 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2:34 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2]))
    block_size_decimal3 = int(hex_str[32 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2:34 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2], 16)
    header_result.extend(process_block_type2("\tData", hex_str[34 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2:34 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3]))

    header_result.extend(process_block_type2("\nblockProtocolExtInfo", hex_str[34 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3:36 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3]))
    header_result.extend(process_block_type2("\tLength", hex_str[36 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3:38 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3]))
    block_size_decimal4 = int(hex_str[36 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3:38 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3], 16)
    header_result.extend(process_block_type2("\tData", hex_str[38 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3:38 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4]))

    header_result.extend(process_block_type2("\nblockRamRomMemory", hex_str[38 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4:40 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4]))
    header_result.extend(process_block_type2("\tLength", hex_str[40 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4:42 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4]))
    block_size_decimal5 = int(hex_str[40 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4:42 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4], 16)
    header_result.extend(process_block_type2("\tData", hex_str[42 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4:42 + sender_size_decimal*2 + 2*block_size_decimal1 + 2*block_size_decimal2 + 2*block_size_decimal3 + 2*block_size_decimal4 + 2*block_size_decimal5]))

    result_dict["Header_Result"] = header_result
    return result_dict

def show_data(request, topic, qos, content_hex):
    
    print(topic)
    print(content_hex)
    print(qos)
    context = run_python_program(topic, qos, content_hex)
    print(context)
    return render(request, "show_data.html", context={'data':context})