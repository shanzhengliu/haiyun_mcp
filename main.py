from typing import Any

from fastmcp import FastMCP
import httpx
# Create a server instance
mcp = FastMCP(name="Delivery Check Service", version="1.0.0")

def check_sea_delivery_one_status(order_id: str) -> dict[Any, Any]:
    """checking delivery status service port 3"""
    url = "http://www.ilsau.cn/track/v1/front/getOrdersTrackWeb"
    payload = {"trackingNos": [order_id]}
    headers = {"content-type": "application/json"}

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)
    result= {}
    if response.status_code != 200:
        raise Exception(f"Error: unknow")
    if response.status_code == 200:
        if not response.json()["body"]:
            return {"status": None, "lastUpdateTime": None}
    result["order_id"] = order_id
    result["type"] = "sea_delivery"
    result["status"] = response.json()["body"][0]["orderStatus"]["Status"]
    result["lastUpdateTime"] = response.json()["body"][0]["orderStatus"]["Lastscan"]
    return result


def check_sea_delivery_two_status(order_id: str) -> dict:
    """checking delivery status service port 2"""
    url = "http://yfd.t6soft.com/trackList"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "page": "1",
        "limit": "10",
        "searchList.waybillnumber": order_id,
        "searchListField.waybillnumber": (
            "border.systemnumber,border.customernumber1,"
            "border.waybillnumber,border.tracknumber,border.newtracknumber"
        ),
        "searchLang": "zh"
    }
    result = {}
    with httpx.Client(verify=False, timeout=10.0) as client:
        response = client.post(url, headers=headers, data=data)
        response.raise_for_status()
        json_data = response.json()
        if not json_data.get("data"):
            return {"status": None, "lastUpdateTime": None}
        result["order_id"] = order_id
        result["type"] = "sea_delivery"
        result["status"] = json_data["data"][0].get("outinfo")
        result["lastUpdateTime"] = json_data["data"][0].get("outdate")
    return result


def query_air_order_status(order_id: str) -> dict:
    """checking delivery status service port 1"""
    url = "http://aun.t6soft.com/trackList"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    data = {
        "page": "1",
        "limit": "10",
        "searchList.waybillnumber": order_id,
        "searchListField.waybillnumber": "border.systemnumber,border.customernumber1,border.waybillnumber,border.tracknumber,border.newtracknumber",
        "searchLang": "zh"
    }

    result = {}
    with httpx.Client(verify=False) as client:
        response = client.post(url, headers=headers, data=data)
        response.raise_for_status()
    if response.status_code != 200:
        raise Exception(f"Error: unknow")
    if len(response.json()["data"]) == 0:
        return {"status": None, "lastUpdateTime": None}
    result["order_id"] = order_id
    result["type"] = "air_delivery"
    result["status"] = response.json()["data"][0]["outinfo"]
    result["lastUpdateTime"] = response.json()["data"][0]["outdate"]
    return result

@mcp.tool
def check_delivery_status(order_id: str) -> dict:
    """Check delivery status for sea and air orders."""
    result = {}
    try:
        query_result = check_sea_delivery_one_status(order_id)
        if query_result["status"] is not None:
            result["sea_delivery_one"] = query_result
            return result
    except Exception as e:
        print("Error checking sea delivery one status: " + order_id)


    try:
        query_result = check_sea_delivery_two_status(order_id)
        if query_result["status"] is not None:
            result["sea_delivery_two"] = query_result
            return result
    except Exception as e:
        print("Error checking sea delivery two status: " + order_id)


    try:
        query_result = query_air_order_status(order_id)
        if query_result["status"] is not None:
            result["air_order"] = query_result
            return result
    except Exception as e:
        print("Error checking air order status: " + order_id)

    return result


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")