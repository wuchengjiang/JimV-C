#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
import json
import jimit as ji
import base64

from api.base import Base
from models import HostCPUMemory, HostTraffic, HostDiskUsageIO, Utils, Rules


__author__ = 'James Iter'
__date__ = '2017/8/7'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_host_performance',
    __name__,
    url_prefix='/api/host_performance'
)

blueprints = Blueprint(
    'api_host_performances',
    __name__,
    url_prefix='/api/host_performances'
)


host_cpu_memory = Base(the_class=HostCPUMemory, the_blueprint=blueprint, the_blueprints=blueprints)
host_traffic = Base(the_class=HostTraffic, the_blueprint=blueprint, the_blueprints=blueprints)
host_disk_usage_io = Base(the_class=HostDiskUsageIO, the_blueprint=blueprint, the_blueprints=blueprints)


@Utils.dumps2response
def r_cpu_memory_get_by_filter():
    return host_cpu_memory.get_by_filter()


@Utils.dumps2response
def r_traffic_get_by_filter():
    return host_traffic.get_by_filter()


@Utils.dumps2response
def r_disk_usage_io_get_by_filter():
    return host_disk_usage_io.get_by_filter()


def get_performance_data(node_id, the_class=None, nic_name=None, mountpoint=None, granularity='hour'):

    args_rules = [
        Rules.NODE_ID.value,
    ]

    filters = list()

    try:
        ji.Check.previewing(args_rules, {'node_id': node_id})

        node_ids_str = 'node_id:in:' + node_id.__str__()
        filters.append(node_ids_str)

        if nic_name is not None:
            filters.append('name:eq:' + nic_name)

        if mountpoint is not None:
            filters.append('mountpoint:eq:' + mountpoint)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        max_limit = 10080
        ts = ji.Common.ts()
        _boundary = ts - 60 * 60
        if granularity == 'hour':
            _boundary = ts - 60 * 60

        elif granularity == 'six_hours':
            _boundary = ts - 60 * 60 * 6

        elif granularity == 'day':
            _boundary = ts - 60 * 60 * 24

        elif granularity == 'seven_days':
            _boundary = ts - 60 * 60 * 24 * 7

        else:
            pass

        filters.append('timestamp:gt:' + _boundary.__str__())

        filter_str = ';'.join(filters)

        _rows, _rows_count = the_class.get_by_filter(
            offset=0, limit=max_limit, order_by='id', order='asc', filter_str=filter_str)

        def smooth_data(boundary=0, interval=60, now_ts=ji.Common.ts(), rows=None):
            needs = list()
            data = list()

            for t in range(boundary + interval, now_ts, interval):
                needs.append(t - t % interval)

            for row in rows:
                if row['timestamp'] % interval != 0:
                    continue

                if needs.__len__() > 0:
                    t = needs.pop(0)
                else:
                    t = now_ts

                while t < row['timestamp']:
                    data.append({
                        'timestamp': t,
                        'cpu_load': None,
                        'memory_available': None,
                        'rx_packets': None,
                        'rx_bytes': None,
                        'tx_packets': None,
                        'tx_bytes': None,
                        'rd_req': None,
                        'rd_bytes': None,
                        'used': None,
                        'wr_req': None,
                        'wr_bytes': None
                    })

                    if needs.__len__() > 0:
                        t = needs.pop(0)
                    else:
                        t = now_ts

                data.append(row)

            return data

        if granularity == 'day':
            ret['data'] = smooth_data(boundary=_boundary, interval=600, now_ts=ts, rows=_rows)

        if granularity == 'seven_days':
            ret['data'] = smooth_data(boundary=_boundary, interval=600, now_ts=ts, rows=_rows)

        else:
            ret['data'] = smooth_data(boundary=_boundary, interval=60, now_ts=ts, rows=_rows)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_cpu_memory_last_hour(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='hour')


@Utils.dumps2response
def r_cpu_memory_last_six_hours(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='six_hours')


@Utils.dumps2response
def r_cpu_memory_last_day(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='day')


@Utils.dumps2response
def r_cpu_memory_last_seven_days(node_id):
    return get_performance_data(node_id=node_id, the_class=HostCPUMemory, granularity='seven_days')


@Utils.dumps2response
def r_traffic_last_hour(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='hour')


@Utils.dumps2response
def r_traffic_last_six_hours(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='six_hours')


@Utils.dumps2response
def r_traffic_last_day(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='day')


@Utils.dumps2response
def r_traffic_last_seven_days(node_id, nic_name):
    return get_performance_data(node_id=node_id, nic_name=nic_name, the_class=HostTraffic, granularity='seven_days')


@Utils.dumps2response
def r_disk_usage_io_last_hour(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO, granularity='hour')


@Utils.dumps2response
def r_disk_usage_io_last_six_hours(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO,
                                granularity='six_hours')


@Utils.dumps2response
def r_disk_usage_io_last_day(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO, granularity='day')


@Utils.dumps2response
def r_disk_usage_io_last_seven_days(node_id, mountpoint):
    mountpoint = base64.b64decode(mountpoint)
    return get_performance_data(node_id=node_id, mountpoint=mountpoint, the_class=HostDiskUsageIO,
                                granularity='seven_days')


@Utils.dumps2response
def r_current_top_10():

    # JimV 设计的 Hosts 容量为 100 个
    volume = 100
    limit = volume
    length = 10
    end_ts = ji.Common.ts() - 60
    start_ts = end_ts - 60

    # 避免落在时间边界上，导致过滤条件的范围落空
    if start_ts % 60 == 0:
        start_ts -= 1

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = {
        'cpu_load': list(),
        'rw_bytes': list(),
        'rw_req': list(),
        'rt_bytes': list(),
        'rt_packets': list()
    }

    filter_str = ';'.join([':'.join(['timestamp', 'gt', start_ts.__str__()]),
                           ':'.join(['timestamp', 'lt', end_ts.__str__()])])

    rows, _ = HostCPUMemory.get_by_filter(limit=limit, filter_str=filter_str)
    rows.sort(key=lambda k: k['cpu_load'], reverse=True)

    effective_range = length
    if rows.__len__() < length:
        effective_range = rows.__len__()

    for i in range(effective_range):
        if rows[i]['cpu_load'] == 0:
            break

        ret['data']['cpu_load'].append(rows[i])

    rows, _ = HostDiskUsageIO.get_by_filter(limit=limit, filter_str=filter_str)
    for i in range(rows.__len__()):
        rows[i]['rw_bytes'] = rows[i]['rd_bytes'] + rows[i]['wr_bytes']
        rows[i]['rw_req'] = rows[i]['rd_req'] + rows[i]['wr_req']

    effective_range = length
    if rows.__len__() < length:
        effective_range = rows.__len__()

    rows.sort(key=lambda k: k['rw_bytes'], reverse=True)

    for i in range(effective_range):
        if rows[i]['rw_req'] == 0:
            break

        ret['data']['rw_bytes'].append(rows[i])

    rows.sort(key=lambda k: k['rw_req'], reverse=True)

    for i in range(effective_range):
        if rows[i]['rw_req'] == 0:
            break

        ret['data']['rw_req'].append(rows[i])

    rows, _ = HostTraffic.get_by_filter(limit=limit, filter_str=filter_str)
    for i in range(rows.__len__()):
        rows[i]['rt_bytes'] = rows[i]['rx_bytes'] + rows[i]['tx_bytes']
        rows[i]['rt_packets'] = rows[i]['rx_packets'] + rows[i]['tx_packets']

    effective_range = length
    if rows.__len__() < length:
        effective_range = rows.__len__()

    rows.sort(key=lambda k: k['rt_bytes'], reverse=True)

    for i in range(effective_range):
        if rows[i]['rt_packets'] == 0:
            break

        ret['data']['rt_bytes'].append(rows[i])

    rows.sort(key=lambda k: k['rt_packets'], reverse=True)

    for i in range(effective_range):
        if rows[i]['rt_packets'] == 0:
            break

        ret['data']['rt_packets'].append(rows[i])

    return ret


@Utils.dumps2response
def r_last_the_range_minutes_top_10(_range):

    volume = 100
    limit = volume * _range
    length = 10
    end_ts = ji.Common.ts() - 60
    start_ts = end_ts - 60 * _range

    # 避免落在时间边界上，导致过滤条件的范围落空
    if start_ts % 60 == 0:
        start_ts -= 1

    ret = dict()
    ret['state'] = ji.Common.exchange_state(20000)
    ret['data'] = {
        'cpu_load': list(),
        'rw_bytes': list(),
        'rw_req': list(),
        'rt_bytes': list(),
        'rt_packets': list()
    }

    filter_str = ';'.join([':'.join(['timestamp', 'gt', start_ts.__str__()]),
                           ':'.join(['timestamp', 'lt', end_ts.__str__()])])

    # cpu 负载
    hosts_node_id_mapping = dict()
    rows, _ = HostCPUMemory.get_by_filter(limit=limit, filter_str=filter_str)
    for row in rows:
        if row['node_id'] not in hosts_node_id_mapping:
            hosts_node_id_mapping[row['node_id']] = {'cpu_load': 0, 'count': 0}

        hosts_node_id_mapping[row['node_id']]['cpu_load'] += row['cpu_load']
        hosts_node_id_mapping[row['node_id']]['count'] += 1.0

    rows = list()
    for k, v in hosts_node_id_mapping.items():

        # 忽略除数为 0 的情况
        if v['cpu_load'] == 0:
            continue

        rows.append({'node_id': k, 'cpu_load': v['cpu_load'] / v['count']})

    effective_range = length
    if rows.__len__() < length:
        effective_range = rows.__len__()

    rows.sort(key=lambda _k: _k['cpu_load'], reverse=True)

    ret['data']['cpu_load'] = rows[0:effective_range]

    # 磁盘使用统计
    hosts_node_id_mapping.clear()
    rows, _ = HostDiskUsageIO.get_by_filter(limit=limit, filter_str=filter_str)
    for row in rows:
        disk_uuid = '_'.join([row['node_id'].__str__(), row['mountpoint']])
        if disk_uuid not in hosts_node_id_mapping:
            hosts_node_id_mapping[disk_uuid] = {'rw_bytes': 0, 'rw_req': 0, 'node_id': row['node_id'],
                                                'mountpoint': row['mountpoint']}

        hosts_node_id_mapping[disk_uuid]['rw_bytes'] += row['rd_bytes'] + row['wr_bytes']
        hosts_node_id_mapping[disk_uuid]['rw_req'] += row['rd_req'] + row['wr_req']

    rows = list()
    for k, v in hosts_node_id_mapping.items():

        # 过滤掉无操作的数据
        if v['rw_req'] == 0:
            continue

        rows.append({'disk_uuid': k, 'rw_bytes': v['rw_bytes'] * 60 * _range, 'rw_req': v['rw_req'] * 60 * _range,
                     'node_id': v['node_id'], 'mountpoint': v['mountpoint']})

    effective_range = length
    if rows.__len__() < length:
        effective_range = rows.__len__()

    rows.sort(key=lambda _k: _k['rw_bytes'], reverse=True)
    ret['data']['rw_bytes'] = rows[0:effective_range]

    rows.sort(key=lambda _k: _k['rw_req'], reverse=True)
    ret['data']['rw_req'] = rows[0:effective_range]

    # 网络流量
    hosts_node_id_mapping.clear()
    rows, _ = HostTraffic.get_by_filter(limit=limit, filter_str=filter_str)
    for row in rows:
        nic_uuid = '_'.join([row['node_id'].__str__(), row['name']])
        if nic_uuid not in hosts_node_id_mapping:
            hosts_node_id_mapping[nic_uuid] = {'rt_bytes': 0, 'rt_packets': 0, 'node_id': row['node_id'],
                                               'name': row['name']}

        hosts_node_id_mapping[nic_uuid]['rt_bytes'] += row['rx_bytes'] + row['tx_bytes']
        hosts_node_id_mapping[nic_uuid]['rt_packets'] += row['rx_packets'] + row['tx_packets']

    rows = list()
    for k, v in hosts_node_id_mapping.items():

        # 过滤掉无流量的数据
        if v['rt_packets'] == 0:
            continue

        rows.append({'nic_uuid': k, 'rt_bytes': v['rt_bytes'] * 60 * _range,
                     'rt_packets': v['rt_packets'] * 60 * _range, 'node_id': v['node_id'], 'name': v['name']})

    effective_range = length
    if rows.__len__() < length:
        effective_range = rows.__len__()

    rows.sort(key=lambda _k: _k['rt_bytes'], reverse=True)
    ret['data']['rt_bytes'] = rows[0:effective_range]

    rows.sort(key=lambda _k: _k['rt_packets'], reverse=True)
    ret['data']['rt_packets'] = rows[0:effective_range]

    return ret


@Utils.dumps2response
def r_last_10_minutes_top_10():
    return r_last_the_range_minutes_top_10(_range=10)


@Utils.dumps2response
def r_last_hour_top_10():
    return r_last_the_range_minutes_top_10(_range=60)


@Utils.dumps2response
def r_last_six_hours_top_10():
    return r_last_the_range_minutes_top_10(_range=60 * 6)


@Utils.dumps2response
def r_last_day_top_10():
    return r_last_the_range_minutes_top_10(_range=60 * 24)


