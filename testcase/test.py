"""
自动生成的 OpenAPI 3.1.0 接口测试用例（正常/异常/高并发三场景）
注意：请根据实际业务调整参数和断言逻辑
"""
import pytest
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time


def test_get_routes_normal():
    """
    【正常场景】测试 Get All Routes
    路径：/routes | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/routes"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'routes' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_routes_abnormal():
    """
    【异常场景】测试 Get All Routes
    路径：/routes | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/routes"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "invalid_param": 'abc',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "invalid_param": "abc"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_routes(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_routes(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_routes(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_routes_concurrency():
    """
    【高并发场景】测试 Get All Routes
    路径：/routes | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/routes"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_routes(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_team_list_normal():
    """
    【正常场景】测试 List Teams
    路径：/team/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "teamId": "valid_team_id_123"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_team_list_abnormal():
    """
    【异常场景】测试 List Teams
    路径：/team/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "teamId": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_team_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_team_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_team_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_team_list_concurrency():
    """
    【高并发场景】测试 List Teams
    路径：/team/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_team_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_team_usr_normal():
    """
    【正常场景】测试 List Team User By Team Id
    路径：/team/usr | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/usr"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "team_id": 123
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_team_usr_abnormal():
    """
    【异常场景】测试 List Team User By Team Id
    路径：/team/usr | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/usr"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "team_id": -1
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_team_usr(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_team_usr(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_team_usr(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_team_usr_concurrency():
    """
    【高并发场景】测试 List Team User By Team Id
    路径：/team/usr | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/usr"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_team_usr(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_team_usr_normal():
    """
    【正常场景】测试 Update Usr Role By Team Id And User Sub
    路径：/team/usr | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/usr"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    "targetUserSub": 'user123',
    "roleId": '123e4567-e89b-12d3-a456-426614174001',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000",
    "targetUserSub": "user123",
    "roleId": "123e4567-e89b-12d3-a456-426614174001"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_team_usr_abnormal():
    """
    【异常场景】测试 Update Usr Role By Team Id And User Sub
    路径：/team/usr | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/usr"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    "targetUserSub": '',
    "roleId": 'also-invalid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid",
    "targetUserSub": "",
    "roleId": "also-invalid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_team_usr(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_team_usr(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_team_usr(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_team_usr_concurrency():
    """
    【高并发场景】测试 Update Usr Role By Team Id And User Sub
    路径：/team/usr | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/usr"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_team_usr(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_team_usr_normal():
    """
    【正常场景】测试 Delete Team User By Team Id And User Subs
    路径：/team/usr | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/usr"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "teamId": "valid_team_id",
    "userSubs": [
        "valid_user_sub"
    ]
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_team_usr_abnormal():
    """
    【异常场景】测试 Delete Team User By Team Id And User Subs
    路径：/team/usr | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/usr"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "teamId": "",
    "userSubs": []
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_team_usr(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_team_usr(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_team_usr(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_team_usr_concurrency():
    """
    【高并发场景】测试 Delete Team User By Team Id And User Subs
    路径：/team/usr | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/usr"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_team_usr(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_team_msg_normal():
    """
    【正常场景】测试 List Team Msg By Team Id
    路径：/team/msg | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/msg"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "teamId": 123,
    "page": 1,
    "size": 10
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_team_msg_abnormal():
    """
    【异常场景】测试 List Team Msg By Team Id
    路径：/team/msg | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/msg"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "teamId": -1,
    "page": -1,
    "size": -5
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_team_msg(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_team_msg(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_team_msg(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_team_msg_concurrency():
    """
    【高并发场景】测试 List Team Msg By Team Id
    路径：/team/msg | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/msg"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_team_msg(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_team_normal():
    """
    【正常场景】测试 Create Team
    路径：/team | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "TestTeam",
    "description": "A test team"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_team_abnormal():
    """
    【异常场景】测试 Create Team
    路径：/team | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "",
    "description": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_team(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_team(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_team(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_team_concurrency():
    """
    【高并发场景】测试 Create Team
    路径：/team | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_team(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_team_normal():
    """
    【正常场景】测试 Update Team By Team Id
    路径：/team | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "Updated Team Name",
    "description": "Updated team description"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json(); assert response.json()['name'] == 'Updated Team Name'
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_team_abnormal():
    """
    【异常场景】测试 Update Team By Team Id
    路径：/team | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid-format',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid-format"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "Invalid Team"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_team(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_team(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_team(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_team_concurrency():
    """
    【高并发场景】测试 Update Team By Team Id
    路径：/team | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_team(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_team_normal():
    """
    【正常场景】测试 Delete Team By Team Id
    路径：/team | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_team_abnormal():
    """
    【异常场景】测试 Delete Team By Team Id
    路径：/team | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_team(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_team(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_team(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_team_concurrency():
    """
    【高并发场景】测试 Delete Team By Team Id
    路径：/team | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_team(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_team_invitation_normal():
    """
    【正常场景】测试 Invite Team User By User Sub
    路径：/team/invitation | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/invitation"
    method = "POST"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "userId": "user123",
    "role": "member"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_team_invitation_abnormal():
    """
    【异常场景】测试 Invite Team User By User Sub
    路径：/team/invitation | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/invitation"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "userId": "user123",
    "role": "member"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_team_invitation(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_team_invitation(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_team_invitation(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_team_invitation_concurrency():
    """
    【高并发场景】测试 Invite Team User By User Sub
    路径：/team/invitation | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/invitation"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_team_invitation(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_team_application_normal():
    """
    【正常场景】测试 Apply To Join Team
    路径：/team/application | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/application"
    method = "POST"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'message' in response.json() or 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_team_application_abnormal():
    """
    【异常场景】测试 Apply To Join Team
    路径：/team/application | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/application"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_team_application(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_team_application(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_team_application(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_team_application_concurrency():
    """
    【高并发场景】测试 Apply To Join Team
    路径：/team/application | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/application"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_team_application(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_team_author_normal():
    """
    【正常场景】测试 Update Team Author By Team Id
    路径：/team/author | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/author"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "targetUserSub": 'user123',
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "targetUserSub": "user123",
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_team_author_abnormal():
    """
    【异常场景】测试 Update Team Author By Team Id
    路径：/team/author | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/team/author"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "targetUserSub": '',
    "teamId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "targetUserSub": "",
    "teamId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_team_author(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_team_author(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_team_author(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_team_author_concurrency():
    """
    【高并发场景】测试 Update Team Author By Team Id
    路径：/team/author | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/team/author"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_team_author(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_kb_normal():
    """
    【正常场景】测试 List Kb By User Sub
    路径：/kb | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "GET"
    
    # 路径参数
    path_params = {
    "kbId": '123e4567-e89b-12d3-a456-426614174000',
    "kbName": 'test_kb',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "kbId": "123e4567-e89b-12d3-a456-426614174000",
    "kbName": "test_kb"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_kb_abnormal():
    """
    【异常场景】测试 List Kb By User Sub
    路径：/kb | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "kbId": 'invalid-uuid-format',
    "kbName": '',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "kbId": "invalid-uuid-format",
    "kbName": ""
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_kb(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_kb(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_kb(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_kb_concurrency():
    """
    【高并发场景】测试 List Kb By User Sub
    路径：/kb | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_kb(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_kb_normal():
    """
    【正常场景】测试 Create Kb
    路径：/kb | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "POST"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "Test KB",
    "description": "Test Knowledge Base"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_kb_abnormal():
    """
    【异常场景】测试 Create Kb
    路径：/kb | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "Test KB",
    "description": "Test Knowledge Base"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_kb(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_kb(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_kb(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_kb_concurrency():
    """
    【高并发场景】测试 Create Kb
    路径：/kb | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_kb(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_kb_normal():
    """
    【正常场景】测试 Update Kb By Kb Id
    路径：/kb | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "kbId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "kbId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "Updated KB",
    "description": "Updated description"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json() or 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_kb_abnormal():
    """
    【异常场景】测试 Update Kb By Kb Id
    路径：/kb | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "kbId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "kbId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "Invalid KB"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_kb(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_kb(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_kb(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_kb_concurrency():
    """
    【高并发场景】测试 Update Kb By Kb Id
    路径：/kb | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_kb(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_kb_normal():
    """
    【正常场景】测试 Delete Kb By Kb Ids
    路径：/kb | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_kb_abnormal():
    """
    【异常场景】测试 Delete Kb By Kb Ids
    路径：/kb | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = [
    "invalid-uuid",
    ""
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'detail' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_kb(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_kb(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_kb(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_kb_concurrency():
    """
    【高并发场景】测试 Delete Kb By Kb Ids
    路径：/kb | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_kb(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_kb_team_normal():
    """
    【正常场景】测试 List Kb By Team Id
    路径：/kb/team | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/team"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert isinstance(response.json(), dict)
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_kb_team_abnormal():
    """
    【异常场景】测试 List Kb By Team Id
    路径：/kb/team | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/team"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_kb_team(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_kb_team(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_kb_team(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_kb_team_concurrency():
    """
    【高并发场景】测试 List Kb By Team Id
    路径：/kb/team | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb/team"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_kb_team(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_kb_doc_type_normal():
    """
    【正常场景】测试 List Doc Types By Kb Id
    路径：/kb/doc_type | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/doc_type"
    method = "GET"
    
    # 路径参数
    path_params = {
    "kbId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "kbId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_kb_doc_type_abnormal():
    """
    【异常场景】测试 List Doc Types By Kb Id
    路径：/kb/doc_type | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/doc_type"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "kbId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "kbId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_kb_doc_type(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_kb_doc_type(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_kb_doc_type(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_kb_doc_type_concurrency():
    """
    【高并发场景】测试 List Doc Types By Kb Id
    路径：/kb/doc_type | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb/doc_type"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_kb_doc_type(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_kb_download_normal():
    """
    【正常场景】测试 Download Kb By Task Id
    路径：/kb/download | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/download"
    method = "GET"
    
    # 路径参数
    path_params = {
    "taskId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "taskId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'content' in response.text or response.headers.get('Content-Type', '').startswith('application/')
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_kb_download_abnormal():
    """
    【异常场景】测试 Download Kb By Task Id
    路径：/kb/download | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/download"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "taskId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "taskId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_kb_download(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_kb_download(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_kb_download(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_kb_download_concurrency():
    """
    【高并发场景】测试 Download Kb By Task Id
    路径：/kb/download | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb/download"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_kb_download(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_kb_import_normal():
    """
    【正常场景】测试 Import Kbs
    路径：/kb/import | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/import"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert isinstance(response.json(), dict)
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_kb_import_abnormal():
    """
    【异常场景】测试 Import Kbs
    路径：/kb/import | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/import"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_kb_import(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_kb_import(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_kb_import(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_kb_import_concurrency():
    """
    【高并发场景】测试 Import Kbs
    路径：/kb/import | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb/import"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_kb_import(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_kb_export_normal():
    """
    【正常场景】测试 Export Kb By Kb Ids
    路径：/kb/export | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/export"
    method = "POST"
    
    # 路径参数
    path_params = {
    "kbIds": ['f47ac10b-58cc-4372-a567-0e02b2c3d479', '123e4567-e89b-12d3-a456-426614174000'],
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "kbIds": [
        "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "123e4567-e89b-12d3-a456-426614174000"
    ]
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_kb_export_abnormal():
    """
    【异常场景】测试 Export Kb By Kb Ids
    路径：/kb/export | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/kb/export"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "kbIds": ['invalid-uuid'],
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "kbIds": [
        "invalid-uuid"
    ]
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_kb_export(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_kb_export(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_kb_export(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_kb_export_concurrency():
    """
    【高并发场景】测试 Export Kb By Kb Ids
    路径：/kb/export | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/kb/export"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_kb_export(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_chunk_list_normal():
    """
    【正常场景】测试 List Chunks By Document Id
    路径：/chunk/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "document_id": "doc_12345"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_chunk_list_abnormal():
    """
    【异常场景】测试 List Chunks By Document Id
    路径：/chunk/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "document_id": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_chunk_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_chunk_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_chunk_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_chunk_list_concurrency():
    """
    【高并发场景】测试 List Chunks By Document Id
    路径：/chunk/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/chunk/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_chunk_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_chunk_search_normal():
    """
    【正常场景】测试 Search Chunks
    路径：/chunk/search | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk/search"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "query": "example search term",
    "page": 1,
    "page_size": 10
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code == 200; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_chunk_search_abnormal():
    """
    【异常场景】测试 Search Chunks
    路径：/chunk/search | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk/search"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "query": "",
    "page": -1,
    "page_size": 0
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_chunk_search(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_chunk_search(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_chunk_search(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_chunk_search_concurrency():
    """
    【高并发场景】测试 Search Chunks
    路径：/chunk/search | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/chunk/search"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_chunk_search(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_chunk_normal():
    """
    【正常场景】测试 Update Chunk By Id
    路径：/chunk | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "chunkId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "chunkId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "content": "updated chunk content",
    "metadata": {
        "key": "value"
    }
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json(); assert response.json()['content'] == 'updated chunk content'
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_chunk_abnormal():
    """
    【异常场景】测试 Update Chunk By Id
    路径：/chunk | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "chunkId": 'invalid-uuid-format',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "chunkId": "invalid-uuid-format"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "content": "some content"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_chunk(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_chunk(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_chunk(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_chunk_concurrency():
    """
    【高并发场景】测试 Update Chunk By Id
    路径：/chunk | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/chunk"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_chunk(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_chunk_switch_normal():
    """
    【正常场景】测试 Update Chunk Enabled By Id
    路径：/chunk/switch | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk/switch"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "enabled": True,
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "enabled": true
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = [
    "550e8400-e29b-41d4-a716-446655440000"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_chunk_switch_abnormal():
    """
    【异常场景】测试 Update Chunk Enabled By Id
    路径：/chunk/switch | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/chunk/switch"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "enabled": 'invalid_bool',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "enabled": "invalid_bool"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = [
    "not-a-uuid"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_chunk_switch(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_chunk_switch(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_chunk_switch(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_chunk_switch_concurrency():
    """
    【高并发场景】测试 Update Chunk Enabled By Id
    路径：/chunk/switch | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/chunk/switch"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_chunk_switch(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_list_normal():
    """
    【正常场景】测试 List Doc
    路径：/doc/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "userId": "12345",
    "docType": "report"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_list_abnormal():
    """
    【异常场景】测试 List Doc
    路径：/doc/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "userId": "",
    "docType": "invalid_type"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_list_concurrency():
    """
    【高并发场景】测试 List Doc
    路径：/doc/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_doc_download_normal():
    """
    【正常场景】测试 Download Doc By Id
    路径：/doc/download | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/download"
    method = "GET"
    
    # 路径参数
    path_params = {
    "docId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "docId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert response.headers.get('Content-Type', '').startswith('application/')
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_doc_download_abnormal():
    """
    【异常场景】测试 Download Doc By Id
    路径：/doc/download | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/download"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "docId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "docId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_doc_download(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_doc_download(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_doc_download(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_doc_download_concurrency():
    """
    【高并发场景】测试 Download Doc By Id
    路径：/doc/download | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/download"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_doc_download(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        success_count = sum(1 for r in results if r.status_code in [200, 201]); assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_doc_report_normal():
    """
    【正常场景】测试 Get Doc Report
    路径：/doc/report | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/report"
    method = "GET"
    
    # 路径参数
    path_params = {
    "docId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "docId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_doc_report_abnormal():
    """
    【异常场景】测试 Get Doc Report
    路径：/doc/report | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/report"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "docId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "docId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_doc_report(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_doc_report(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_doc_report(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_doc_report_concurrency():
    """
    【高并发场景】测试 Get Doc Report
    路径：/doc/report | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/report"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_doc_report(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_doc_report_download_normal():
    """
    【正常场景】测试 Download Doc Report
    路径：/doc/report/download | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/report/download"
    method = "GET"
    
    # 路径参数
    path_params = {
    "docId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "docId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert response.headers.get('Content-Type', '').startswith('application/')
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_doc_report_download_abnormal():
    """
    【异常场景】测试 Download Doc Report
    路径：/doc/report/download | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/report/download"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "docId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "docId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_doc_report_download(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_doc_report_download(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_doc_report_download(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_doc_report_download_concurrency():
    """
    【高并发场景】测试 Download Doc Report
    路径：/doc/report/download | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/report/download"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_doc_report_download(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_normal():
    """
    【正常场景】测试 Upload Docs
    路径：/doc | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert isinstance(response.json(), dict)
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_abnormal():
    """
    【异常场景】测试 Upload Docs
    路径：/doc | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_concurrency():
    """
    【高并发场景】测试 Upload Docs
    路径：/doc | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_doc_normal():
    """
    【正常场景】测试 Update Doc By Doc Id
    路径：/doc | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "docId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "docId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "title": "Updated Title",
    "content": "Updated content"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_doc_abnormal():
    """
    【异常场景】测试 Update Doc By Doc Id
    路径：/doc | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "docId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "docId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "title": "Bad Request",
    "content": "Invalid docId format"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_doc(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_doc(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_doc(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_doc_concurrency():
    """
    【高并发场景】测试 Update Doc By Doc Id
    路径：/doc | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_doc(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_doc_normal():
    """
    【正常场景】测试 Delete Docs By Ids
    路径：/doc | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_doc_abnormal():
    """
    【异常场景】测试 Delete Docs By Ids
    路径：/doc | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = [
    "invalid-uuid",
    ""
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_doc(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_doc(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_doc(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_doc_concurrency():
    """
    【高并发场景】测试 Delete Docs By Ids
    路径：/doc | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_doc(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_parse_normal():
    """
    【正常场景】测试 Parse Docuement By Doc Ids
    路径：/doc/parse | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/parse"
    method = "POST"
    
    # 路径参数
    path_params = {
    "parse": True,
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "parse": true
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = [
    "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "123e4567-e89b-12d3-a456-426614174000"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_parse_abnormal():
    """
    【异常场景】测试 Parse Docuement By Doc Ids
    路径：/doc/parse | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/parse"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "parse": True,
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "parse": true
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = [
    ""
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc_parse(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc_parse(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc_parse(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_parse_concurrency():
    """
    【高并发场景】测试 Parse Docuement By Doc Ids
    路径：/doc/parse | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/parse"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc_parse(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_metadata_normal():
    """
    【正常场景】测试 Parse Docuement Realtime
    路径：/doc/metadata | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/metadata"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "file": "<valid_file_content>"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'metadata' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_metadata_abnormal():
    """
    【异常场景】测试 Parse Docuement Realtime
    路径：/doc/metadata | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/metadata"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "file": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc_metadata(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc_metadata(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc_metadata(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_metadata_concurrency():
    """
    【高并发场景】测试 Parse Docuement Realtime
    路径：/doc/metadata | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/metadata"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc_metadata(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_temporary_status_normal():
    """
    【正常场景】测试 Get Temporary Docs Status
    路径：/doc/temporary/status | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/status"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "documentIds": [
        "doc123",
        "doc456"
    ]
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'status' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_temporary_status_abnormal():
    """
    【异常场景】测试 Get Temporary Docs Status
    路径：/doc/temporary/status | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/status"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "documentIds": []
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc_temporary_status(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc_temporary_status(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc_temporary_status(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_temporary_status_concurrency():
    """
    【高并发场景】测试 Get Temporary Docs Status
    路径：/doc/temporary/status | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/temporary/status"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc_temporary_status(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_temporary_parser_normal():
    """
    【正常场景】测试 Upload Temporary Docs
    路径：/doc/temporary/parser | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/parser"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "file_name": "test.pdf",
    "content_type": "application/pdf",
    "file_data": "base64_encoded_string"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'file_id' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_temporary_parser_abnormal():
    """
    【异常场景】测试 Upload Temporary Docs
    路径：/doc/temporary/parser | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/parser"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "file_name": "",
    "content_type": "",
    "file_data": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc_temporary_parser(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc_temporary_parser(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc_temporary_parser(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_temporary_parser_concurrency():
    """
    【高并发场景】测试 Upload Temporary Docs
    路径：/doc/temporary/parser | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/temporary/parser"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc_temporary_parser(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_doc_temporary_text_normal():
    """
    【正常场景】测试 Get Temporary Docs Text
    路径：/doc/temporary/text | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/text"
    method = "GET"
    
    # 路径参数
    path_params = {
    "id": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "id": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'text' in response.json() or 'content' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_doc_temporary_text_abnormal():
    """
    【异常场景】测试 Get Temporary Docs Text
    路径：/doc/temporary/text | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/text"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "id": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "id": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_doc_temporary_text(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_doc_temporary_text(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_doc_temporary_text(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_doc_temporary_text_concurrency():
    """
    【高并发场景】测试 Get Temporary Docs Text
    路径：/doc/temporary/text | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/temporary/text"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_doc_temporary_text(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_temporary_delete_normal():
    """
    【正常场景】测试 Delete Temporary Docs
    路径：/doc/temporary/delete | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/delete"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "docIds": [
        "temp_doc_123"
    ]
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_temporary_delete_abnormal():
    """
    【异常场景】测试 Delete Temporary Docs
    路径：/doc/temporary/delete | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/temporary/delete"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "docIds": []
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc_temporary_delete(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc_temporary_delete(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc_temporary_delete(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_temporary_delete_concurrency():
    """
    【高并发场景】测试 Delete Temporary Docs
    路径：/doc/temporary/delete | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/temporary/delete"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc_temporary_delete(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_doc_speed_test_normal():
    """
    【正常场景】测试 Upload Speed Test
    路径：/doc/speed-test | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/speed-test"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "file": "test_file.txt"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'upload_id' in response.json() or 'speed' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_doc_speed_test_abnormal():
    """
    【异常场景】测试 Upload Speed Test
    路径：/doc/speed-test | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/doc/speed-test"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "file": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'detail' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_doc_speed_test(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_doc_speed_test(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_doc_speed_test(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_doc_speed_test_concurrency():
    """
    【高并发场景】测试 Upload Speed Test
    路径：/doc/speed-test | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/doc/speed-test"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_doc_speed_test(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_health_check_normal():
    """
    【正常场景】测试 Health Check
    路径：/health_check | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/health_check"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'status' in response.json() and response.json()['status'] == 'ok'
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_health_check_abnormal():
    """
    【异常场景】测试 Health Check
    路径：/health_check | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/health_check"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_health_check(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_health_check(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_health_check(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_health_check_concurrency():
    """
    【高并发场景】测试 Health Check
    路径：/health_check | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/health_check"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_health_check(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_dataset_list_normal():
    """
    【正常场景】测试 List Dataset By Kb Id
    路径：/dataset/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "kb_id": "valid_kb_123"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_dataset_list_abnormal():
    """
    【异常场景】测试 List Dataset By Kb Id
    路径：/dataset/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "kb_id": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_dataset_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_dataset_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_dataset_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_dataset_list_concurrency():
    """
    【高并发场景】测试 List Dataset By Kb Id
    路径：/dataset/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_dataset_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_dataset_data_normal():
    """
    【正常场景】测试 List Data In Dataset
    路径：/dataset/data | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/data"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "dataset_id": "valid_dataset_123",
    "page": 1,
    "page_size": 10
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json(); assert isinstance(response.json()['data'], list)
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_dataset_data_abnormal():
    """
    【异常场景】测试 List Data In Dataset
    路径：/dataset/data | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/data"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "dataset_id": "",
    "page": -1,
    "page_size": 0
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_dataset_data(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_dataset_data(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_dataset_data(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_dataset_data_concurrency():
    """
    【高并发场景】测试 List Data In Dataset
    路径：/dataset/data | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/data"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_dataset_data(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_dataset_data_normal():
    """
    【正常场景】测试 Update Data By Dataset Id
    路径：/dataset/data | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/data"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "dataId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "dataId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "updated_data",
    "value": "new_value"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_dataset_data_abnormal():
    """
    【异常场景】测试 Update Data By Dataset Id
    路径：/dataset/data | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/data"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "dataId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "dataId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "test",
    "value": "value"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_dataset_data(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_dataset_data(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_dataset_data(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_dataset_data_concurrency():
    """
    【高并发场景】测试 Update Data By Dataset Id
    路径：/dataset/data | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/data"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_dataset_data(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_dataset_data_normal():
    """
    【正常场景】测试 Delete Data By Data Ids
    路径：/dataset/data | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/data"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_dataset_data_abnormal():
    """
    【异常场景】测试 Delete Data By Data Ids
    路径：/dataset/data | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/data"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = [
    "invalid-uuid",
    ""
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_dataset_data(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_dataset_data(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_dataset_data(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_dataset_data_concurrency():
    """
    【高并发场景】测试 Delete Data By Data Ids
    路径：/dataset/data | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/data"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_dataset_data(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_dataset_testing_exist_normal():
    """
    【正常场景】测试 Is Dataset Have Testing
    路径：/dataset/testing/exist | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/testing/exist"
    method = "GET"
    
    # 路径参数
    path_params = {
    "datasetId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "datasetId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_dataset_testing_exist_abnormal():
    """
    【异常场景】测试 Is Dataset Have Testing
    路径：/dataset/testing/exist | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/testing/exist"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "datasetId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "datasetId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_dataset_testing_exist(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_dataset_testing_exist(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_dataset_testing_exist(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_dataset_testing_exist_concurrency():
    """
    【高并发场景】测试 Is Dataset Have Testing
    路径：/dataset/testing/exist | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/testing/exist"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_dataset_testing_exist(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_dataset_download_normal():
    """
    【正常场景】测试 Download Dataset By Task Id
    路径：/dataset/download | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/download"
    method = "GET"
    
    # 路径参数
    path_params = {
    "taskId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "taskId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert response.headers.get('Content-Type', '').startswith('application/')
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_dataset_download_abnormal():
    """
    【异常场景】测试 Download Dataset By Task Id
    路径：/dataset/download | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/download"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "taskId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "taskId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.text or 'message' in response.text
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_dataset_download(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_dataset_download(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_dataset_download(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_dataset_download_concurrency():
    """
    【高并发场景】测试 Download Dataset By Task Id
    路径：/dataset/download | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/download"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_dataset_download(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        success_count = sum(1 for r in results if r.status_code in [200, 201]); assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_dataset_normal():
    """
    【正常场景】测试 Create Dataset
    路径：/dataset | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "test_dataset",
    "description": "This is a test dataset"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_dataset_abnormal():
    """
    【异常场景】测试 Create Dataset
    路径：/dataset | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "",
    "description": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_dataset(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_dataset(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_dataset(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_dataset_concurrency():
    """
    【高并发场景】测试 Create Dataset
    路径：/dataset | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_dataset(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_dataset_normal():
    """
    【正常场景】测试 Update Dataset By Dataset Id
    路径：/dataset | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "databaseId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "databaseId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "updated_dataset",
    "description": "Updated dataset description"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_dataset_abnormal():
    """
    【异常场景】测试 Update Dataset By Dataset Id
    路径：/dataset | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "databaseId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "databaseId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "invalid_dataset"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_dataset(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_dataset(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_dataset(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_dataset_concurrency():
    """
    【高并发场景】测试 Update Dataset By Dataset Id
    路径：/dataset | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_dataset(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_dataset_normal():
    """
    【正常场景】测试 Delete Dataset By Dataset Ids
    路径：/dataset | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_dataset_abnormal():
    """
    【异常场景】测试 Delete Dataset By Dataset Ids
    路径：/dataset | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = [
    "invalid-uuid",
    ""
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_dataset(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_dataset(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_dataset(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_dataset_concurrency():
    """
    【高并发场景】测试 Delete Dataset By Dataset Ids
    路径：/dataset | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_dataset(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_dataset_import_normal():
    """
    【正常场景】测试 Import Dataset
    路径：/dataset/import | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/import"
    method = "POST"
    
    # 路径参数
    path_params = {
    "kbId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "kbId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "file": "<file_content>"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_dataset_import_abnormal():
    """
    【异常场景】测试 Import Dataset
    路径：/dataset/import | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/import"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "kbId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "kbId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "file": "<file_content>"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_dataset_import(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_dataset_import(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_dataset_import(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_dataset_import_concurrency():
    """
    【高并发场景】测试 Import Dataset
    路径：/dataset/import | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/import"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_dataset_import(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_dataset_export_normal():
    """
    【正常场景】测试 Export Dataset By Dataset Ids
    路径：/dataset/export | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/export"
    method = "POST"
    
    # 路径参数
    path_params = {
    "datasetIds": ['123e4567-e89b-12d3-a456-426614174000'],
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "datasetIds": [
        "123e4567-e89b-12d3-a456-426614174000"
    ]
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_dataset_export_abnormal():
    """
    【异常场景】测试 Export Dataset By Dataset Ids
    路径：/dataset/export | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/export"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "datasetIds": ['invalid-uuid'],
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "datasetIds": [
        "invalid-uuid"
    ]
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_dataset_export(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_dataset_export(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_dataset_export(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_dataset_export_concurrency():
    """
    【高并发场景】测试 Export Dataset By Dataset Ids
    路径：/dataset/export | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/export"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_dataset_export(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_dataset_generate_normal():
    """
    【正常场景】测试 Generate Dataset By Id
    路径：/dataset/generate | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/generate"
    method = "POST"
    
    # 路径参数
    path_params = {
    "datasetId": '123e4567-e89b-12d3-a456-426614174000',
    "generate": True,
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "datasetId": "123e4567-e89b-12d3-a456-426614174000",
    "generate": true
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_dataset_generate_abnormal():
    """
    【异常场景】测试 Generate Dataset By Id
    路径：/dataset/generate | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/dataset/generate"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "datasetId": 'invalid-uuid',
    "generate": True,
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "datasetId": "invalid-uuid",
    "generate": true
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_dataset_generate(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_dataset_generate(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_dataset_generate(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_dataset_generate_concurrency():
    """
    【高并发场景】测试 Generate Dataset By Id
    路径：/dataset/generate | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/dataset/generate"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_dataset_generate(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_other_llm_normal():
    """
    【正常场景】测试 List Llms By User Sub
    路径：/other/llm | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/llm"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code == 200; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_other_llm_abnormal():
    """
    【异常场景】测试 List Llms By User Sub
    路径：/other/llm | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/llm"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_other_llm(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_other_llm(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_other_llm(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_other_llm_concurrency():
    """
    【高并发场景】测试 List Llms By User Sub
    路径：/other/llm | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/other/llm"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_other_llm(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_other_embedding_normal():
    """
    【正常场景】测试 List Embeddings
    路径：/other/embedding | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/embedding"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_other_embedding_abnormal():
    """
    【异常场景】测试 List Embeddings
    路径：/other/embedding | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/embedding"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_other_embedding(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_other_embedding(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_other_embedding(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_other_embedding_concurrency():
    """
    【高并发场景】测试 List Embeddings
    路径：/other/embedding | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/other/embedding"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_other_embedding(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_other_rerank_normal():
    """
    【正常场景】测试 List Reranks
    路径：/other/rerank | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/rerank"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_other_rerank_abnormal():
    """
    【异常场景】测试 List Reranks
    路径：/other/rerank | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/rerank"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_other_rerank(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_other_rerank(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_other_rerank(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_other_rerank_concurrency():
    """
    【高并发场景】测试 List Reranks
    路径：/other/rerank | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/other/rerank"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_other_rerank(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_other_tokenizer_normal():
    """
    【正常场景】测试 List Tokenizers
    路径：/other/tokenizer | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/tokenizer"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'tokenizers' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_other_tokenizer_abnormal():
    """
    【异常场景】测试 List Tokenizers
    路径：/other/tokenizer | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/tokenizer"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "invalid_param": 'invalid_value',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "invalid_param": "invalid_value"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_other_tokenizer(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_other_tokenizer(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_other_tokenizer(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_other_tokenizer_concurrency():
    """
    【高并发场景】测试 List Tokenizers
    路径：/other/tokenizer | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/other/tokenizer"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_other_tokenizer(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_other_parse_method_normal():
    """
    【正常场景】测试 List Parse Method
    路径：/other/parse_method | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/parse_method"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_other_parse_method_abnormal():
    """
    【异常场景】测试 List Parse Method
    路径：/other/parse_method | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/parse_method"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "invalid_param": '',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "invalid_param": ""
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_other_parse_method(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_other_parse_method(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_other_parse_method(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_other_parse_method_concurrency():
    """
    【高并发场景】测试 List Parse Method
    路径：/other/parse_method | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/other/parse_method"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_other_parse_method(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_other_search_method_normal():
    """
    【正常场景】测试 List Search Method
    路径：/other/search_method | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/search_method"
    method = "GET"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_other_search_method_abnormal():
    """
    【异常场景】测试 List Search Method
    路径：/other/search_method | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/other/search_method"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "invalid_param": 'invalid_value',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "invalid_param": "invalid_value"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_other_search_method(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_other_search_method(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_other_search_method(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_other_search_method_concurrency():
    """
    【高并发场景】测试 List Search Method
    路径：/other/search_method | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/other/search_method"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_other_search_method(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_testing_list_normal():
    """
    【正常场景】测试 List Testing By Kb Id
    路径：/testing/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "kb_id": "valid_kb_123"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_testing_list_abnormal():
    """
    【异常场景】测试 List Testing By Kb Id
    路径：/testing/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "kb_id": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_testing_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_testing_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_testing_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_testing_list_concurrency():
    """
    【高并发场景】测试 List Testing By Kb Id
    路径：/testing/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/testing/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_testing_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_testing_testcase_normal():
    """
    【正常场景】测试 List Testcase By Testing Id
    路径：/testing/testcase | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/testcase"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "testing_id": 123
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_testing_testcase_abnormal():
    """
    【异常场景】测试 List Testcase By Testing Id
    路径：/testing/testcase | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/testcase"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "testing_id": -1
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_testing_testcase(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_testing_testcase(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_testing_testcase(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_testing_testcase_concurrency():
    """
    【高并发场景】测试 List Testcase By Testing Id
    路径：/testing/testcase | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/testing/testcase"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_testing_testcase(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_testing_download_normal():
    """
    【正常场景】测试 Download Testing Report By Testing Id
    路径：/testing/download | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/download"
    method = "GET"
    
    # 路径参数
    path_params = {
    "testingId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "testingId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert response.headers.get('Content-Type', '').startswith('application/')
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_testing_download_abnormal():
    """
    【异常场景】测试 Download Testing Report By Testing Id
    路径：/testing/download | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/download"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "testingId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "testingId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.text or 'message' in response.text
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_testing_download(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_testing_download(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_testing_download(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_testing_download_concurrency():
    """
    【高并发场景】测试 Download Testing Report By Testing Id
    路径：/testing/download | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/testing/download"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_testing_download(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_testing_normal():
    """
    【正常场景】测试 Create Testing
    路径：/testing | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "test",
    "value": 123
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_testing_abnormal():
    """
    【异常场景】测试 Create Testing
    路径：/testing | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "",
    "value": null
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_testing(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_testing(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_testing(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_testing_concurrency():
    """
    【高并发场景】测试 Create Testing
    路径：/testing | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/testing"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_testing(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_testing_normal():
    """
    【正常场景】测试 Update Testing By Testing Id
    路径：/testing | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "testingId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "testingId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "Updated Testing",
    "status": "active"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_testing_abnormal():
    """
    【异常场景】测试 Update Testing By Testing Id
    路径：/testing | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "testingId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "testingId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "Invalid Testing",
    "status": "active"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_testing(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_testing(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_testing(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_testing_concurrency():
    """
    【高并发场景】测试 Update Testing By Testing Id
    路径：/testing | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/testing"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_testing(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_testing_normal():
    """
    【正常场景】测试 Delete Testing By Testing Ids
    路径：/testing | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_testing_abnormal():
    """
    【异常场景】测试 Delete Testing By Testing Ids
    路径：/testing | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = [
    "invalid-uuid",
    ""
]
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_testing(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_testing(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_testing(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_testing_concurrency():
    """
    【高并发场景】测试 Delete Testing By Testing Ids
    路径：/testing | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/testing"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_testing(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_testing_run_normal():
    """
    【正常场景】测试 Run Testing By Testing Id
    路径：/testing/run | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/run"
    method = "POST"
    
    # 路径参数
    path_params = {
    "testingId": '123e4567-e89b-12d3-a456-426614174000',
    "run": True,
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "testingId": "123e4567-e89b-12d3-a456-426614174000",
    "run": true
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_testing_run_abnormal():
    """
    【异常场景】测试 Run Testing By Testing Id
    路径：/testing/run | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/testing/run"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "testingId": 'invalid-uuid',
    "run": True,
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "testingId": "invalid-uuid",
    "run": true
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_testing_run(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_testing_run(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_testing_run(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_testing_run_concurrency():
    """
    【高并发场景】测试 Run Testing By Testing Id
    路径：/testing/run | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/testing/run"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_testing_run(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_role_action_normal():
    """
    【正常场景】测试 List Actions
    路径：/role/action | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role/action"
    method = "GET"
    
    # 路径参数
    path_params = {
    "language": 'zh',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "language": "zh"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code == 200; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_role_action_abnormal():
    """
    【异常场景】测试 List Actions
    路径：/role/action | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role/action"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "language": 'invalid_lang',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "language": "invalid_lang"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_role_action(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_role_action(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_role_action(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_role_action_concurrency():
    """
    【高并发场景】测试 List Actions
    路径：/role/action | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/role/action"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_role_action(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_role_normal():
    """
    【正常场景】测试 Get User Role
    路径：/role | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "GET"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'role' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_role_abnormal():
    """
    【异常场景】测试 Get User Role
    路径：/role | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_role(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_role(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_role(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_role_concurrency():
    """
    【高并发场景】测试 Get User Role
    路径：/role | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/role"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_role(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_role_normal():
    """
    【正常场景】测试 Create Role
    路径：/role | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "POST"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "Admin",
    "permissions": [
        "read",
        "write"
    ]
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json(); assert response.json()['name'] == 'Admin'
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_role_abnormal():
    """
    【异常场景】测试 Create Role
    路径：/role | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "InvalidRole",
    "permissions": []
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_role(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_role(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_role(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_role_concurrency():
    """
    【高并发场景】测试 Create Role
    路径：/role | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/role"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_role(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_role_normal():
    """
    【正常场景】测试 Update Role By Role Id
    路径：/role | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "roleId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "roleId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "name": "Admin",
    "permissions": [
        "read",
        "write"
    ]
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'id' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_role_abnormal():
    """
    【异常场景】测试 Update Role By Role Id
    路径：/role | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "roleId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "roleId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "name": "",
    "permissions": []
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_role(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_role(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_role(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_role_concurrency():
    """
    【高并发场景】测试 Update Role By Role Id
    路径：/role | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/role"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_role(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_role_normal():
    """
    【正常场景】测试 Delete Role By Role Ids
    路径：/role | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    "roleId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "roleId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_role_abnormal():
    """
    【异常场景】测试 Delete Role By Role Ids
    路径：/role | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    "roleId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "roleId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_role(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_role(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_role(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_role_concurrency():
    """
    【高并发场景】测试 Delete Role By Role Ids
    路径：/role | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/role"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_role(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_role_list_normal():
    """
    【正常场景】测试 List Roles
    路径：/role/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert isinstance(response.json(), dict)
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_role_list_abnormal():
    """
    【异常场景】测试 List Roles
    路径：/role/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/role/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_role_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_role_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_role_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_role_list_concurrency():
    """
    【高并发场景】测试 List Roles
    路径：/role/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/role/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_role_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_get_usr_msg_exist_normal():
    """
    【正常场景】测试 Is User Message Exist
    路径：/usr_msg/exist | 方法：GET
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg/exist"
    method = "GET"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    "msgType": 'NOTICE',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000",
    "msgType": "NOTICE"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'exists' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_get_usr_msg_exist_abnormal():
    """
    【异常场景】测试 Is User Message Exist
    路径：/usr_msg/exist | 方法：GET
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg/exist"
    method = "GET"
    
    # 非法路径参数
    path_params = {
    "teamId": 'invalid-uuid',
    "msgType": '',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "invalid-uuid",
    "msgType": ""
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_get_usr_msg_exist(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_get_usr_msg_exist(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_get_usr_msg_exist(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_get_usr_msg_exist_concurrency():
    """
    【高并发场景】测试 Is User Message Exist
    路径：/usr_msg/exist | 方法：GET
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/usr_msg/exist"
    method = "GET"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_get_usr_msg_exist(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_usr_msg_list_normal():
    """
    【正常场景】测试 List User Msgs By User Sub
    路径：/usr_msg/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "user_sub": "valid_user_sub_123"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_usr_msg_list_abnormal():
    """
    【异常场景】测试 List User Msgs By User Sub
    路径：/usr_msg/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "user_sub": ""
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_usr_msg_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_usr_msg_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_usr_msg_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_usr_msg_list_concurrency():
    """
    【高并发场景】测试 List User Msgs By User Sub
    路径：/usr_msg/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/usr_msg/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_usr_msg_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_put_usr_msg_normal():
    """
    【正常场景】测试 Update User Msg By Msg Id
    路径：/usr_msg | 方法：PUT
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg"
    method = "PUT"
    
    # 路径参数
    path_params = {
    "msgId": '123e4567-e89b-12d3-a456-426614174000',
    "msgStatus": 'READ',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "msgId": "123e4567-e89b-12d3-a456-426614174000",
    "msgStatus": "READ"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_put_usr_msg_abnormal():
    """
    【异常场景】测试 Update User Msg By Msg Id
    路径：/usr_msg | 方法：PUT
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg"
    method = "PUT"
    
    # 非法路径参数
    path_params = {
    "msgId": 'invalid-uuid',
    "msgStatus": '',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "msgId": "invalid-uuid",
    "msgStatus": ""
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_put_usr_msg(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_put_usr_msg(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_put_usr_msg(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_put_usr_msg_concurrency():
    """
    【高并发场景】测试 Update User Msg By Msg Id
    路径：/usr_msg | 方法：PUT
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/usr_msg"
    method = "PUT"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_put_usr_msg(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_usr_msg_normal():
    """
    【正常场景】测试 Delete User Msg By Msg Ids
    路径：/usr_msg | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    "msgId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "msgId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or response.json().get('code') in [200, 201]
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_usr_msg_abnormal():
    """
    【异常场景】测试 Delete User Msg By Msg Ids
    路径：/usr_msg | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/usr_msg"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    "msgId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "msgId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_usr_msg(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_usr_msg(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_usr_msg(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_usr_msg_concurrency():
    """
    【高并发场景】测试 Delete User Msg By Msg Ids
    路径：/usr_msg | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/usr_msg"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_usr_msg(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_task_normal():
    """
    【正常场景】测试 List Task
    路径：/task | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/task"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = {
    "task_id": "valid_task_123",
    "status": "pending"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'data' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_task_abnormal():
    """
    【异常场景】测试 List Task
    路径：/task | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/task"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {
    "task_id": "",
    "status": "invalid_status"
}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_task(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_task(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_task(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_task_concurrency():
    """
    【高并发场景】测试 List Task
    路径：/task | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/task"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_task(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_task_one_normal():
    """
    【正常场景】测试 Delete Task By Task Id
    路径：/task/one | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/task/one"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    "taskId": '123e4567-e89b-12d3-a456-426614174000',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "taskId": "123e4567-e89b-12d3-a456-426614174000"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_task_one_abnormal():
    """
    【异常场景】测试 Delete Task By Task Id
    路径：/task/one | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/task/one"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    "taskId": 'invalid-uuid',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "taskId": "invalid-uuid"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_task_one(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_task_one(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_task_one(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_task_one_concurrency():
    """
    【高并发场景】测试 Delete Task By Task Id
    路径：/task/one | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/task/one"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_task_one(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_delete_task_all_normal():
    """
    【正常场景】测试 Delete Task By Task Type
    路径：/task/all | 方法：DELETE
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/task/all"
    method = "DELETE"
    
    # 路径参数
    path_params = {
    "teamId": '123e4567-e89b-12d3-a456-426614174000',
    "taskType": 'DAILY',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 请求参数
    params = {
    "teamId": "123e4567-e89b-12d3-a456-426614174000",
    "taskType": "DAILY"
}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert 'success' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_delete_task_all_abnormal():
    """
    【异常场景】测试 Delete Task By Task Type
    路径：/task/all | 方法：DELETE
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/task/all"
    method = "DELETE"
    
    # 非法路径参数
    path_params = {
    "teamId": '',
    "taskType": 'INVALID_TYPE',
    }

    # 替换路径参数
    for key, value in path_params.items():
        url = url.replace(f"{{{{key}}}}", str(value))

    # 非法请求参数
    params = {
    "teamId": "",
    "taskType": "INVALID_TYPE"
}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert response.status_code in [400, 404, 403]; assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_delete_task_all(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_delete_task_all(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_delete_task_all(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_delete_task_all_concurrency():
    """
    【高并发场景】测试 Delete Task By Task Type
    路径：/task/all | 方法：DELETE
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/task/all"
    method = "DELETE"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_delete_task_all(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


def test_post_user_list_normal():
    """
    【正常场景】测试 List Users
    路径：/user/list | 方法：POST
    场景：合法参数请求，校验接口正常响应
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/user/list"
    method = "POST"
    
    # 路径参数
    path_params = {
    # 无路径参数
    }

    # 请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 请求体
    data = None
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"正常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 断言逻辑
    try:
        assert response.status_code in [200, 201]; assert isinstance(response.json(), dict)
    except Exception as e:
        pytest.fail(f"正常场景断言失败：{str(e)}")
    print(f"正常场景测试通过：{response.status_code}")


def test_post_user_list_abnormal():
    """
    【异常场景】测试 List Users
    路径：/user/list | 方法：POST
    场景：非法参数请求，校验错误处理
    """
    # 初始化response变量，避免未定义
    response = None
    url = "http://localhost:9988/user/list"
    method = "POST"
    
    # 非法路径参数
    path_params = {
    # 无非法路径参数（使用空值模拟）
    "id": "invalid_123",
    }

    # 非法请求参数
    params = {}
    headers = {"Content-Type": "application/json"}
    
    # 非法请求体
    data = {'id': '', 'name': None}
    
    # 发送请求
    try:
        response = requests.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"异常场景请求失败：{str(e)}")
    
    # 确保response已定义
    assert response is not None, "请求未返回响应"
    
    # 基础异常断言
    try:
        assert response.status_code == 400, f"预期状态码{400}，实际{response.status_code}"
    except AssertionError as e:
        pytest.fail(f"异常场景状态码断言失败：{str(e)}")
    
    # 业务异常断言
    try:
        assert 'error' in response.json() or 'message' in response.json()
    except Exception as e:
        pytest.fail(f"异常场景业务断言失败：{str(e)}")
    print(f"异常场景测试通过：{response.status_code}")


async def _async_request_post_user_list(session, url, method, params, data, headers):
    """异步请求函数"""
    try:
        async with session.request(
            method=method.lower(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=30
        ) as response:
            return {
                "status": response.status,
                "success": response.status in [200, 201],
                "error": None
            }
    except Exception as e:
        return {"status": 0, "success": False, "error": str(e)}

async def _run_concurrent_tests_post_user_list(url, method, params, data, headers, count):
    """运行并发测试"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(count):
            task = _async_request_post_user_list(session, url, method, params, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results

def test_post_user_list_concurrency():
    """
    【高并发场景】测试 List Users
    路径：/user/list | 方法：POST
    场景：模拟100次并发请求，校验接口稳定性
    """
    # 初始化所有变量
    results = []
    success_count = 0
    fail_count = 0
    avg_time = 0
    
    url = "http://localhost:9988/user/list"
    method = "POST"
    
    # 基准参数（正常场景参数）
    path_params = {}
    
    # 无路径参数需要替换

    params = {}
    headers = {"Content-Type": "application/json"}
    data = {}  # 正常场景默认请求体
    
    # 运行并发测试
    try:
        start_time = time.time()
        results = asyncio.run(_run_concurrent_tests_post_user_list(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
            count=100
        ))
        end_time = time.time()
    except Exception as e:
        pytest.fail(f"并发测试执行失败：{str(e)}")
    
    # 确保结果已定义
    assert isinstance(results, list), "并发测试结果格式错误"
    assert len(results) == 100, f"并发测试结果数量异常：{len(results)}"
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = 100 - success_count
    avg_time = (end_time - start_time) / 100
    
    # 并发断言
    print(f"并发测试完成：成功{success_count}/{100}，失败{fail_count}，平均耗时{avg_time:.4f}秒")
    try:
        assert success_count >= 95
        assert fail_count <= 5, f"并发失败数超过阈值：{fail_count}"
        assert avg_time < 0.1, f"平均响应时间过长：{avg_time:.4f}秒"
    except AssertionError as e:
        pytest.fail(f"并发场景断言失败：{str(e)}")


if __name__ == "__main__":
    # 运行所有测试
    pytest.main(["-v", __file__, "-s"])
    # 单独运行某个场景：pytest -v __file__::test_xxx_normal
