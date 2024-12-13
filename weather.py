import requests
from datetime import datetime

def get_weather_forecast(location, target_time, api_key):
    try:
        # API URL
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization={api_key}&format=JSON"
        
        # 發送請求取得資料
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return {"error": f"無法取得天氣資料，狀態碼：{response.status_code}"}
        
        data = response.json()
        
        # 找到指定地點
        for location_data in data['records']['locations'][0]['location']:
            if location_data['locationName'] == location:
                weather_info = {}
                for element in location_data['weatherElement']:
                    element_name = element['elementName']
                    
                    # 搜尋符合時間的預報資料
                    for time_data in element['time']:
                        start_time = time_data['startTime']
                        if target_time in start_time:
                            weather_info[element_name] = time_data['elementValue'][0]['value']
                
                # 提取必要的元素
                weather_data = {
                    "最低溫度 (MinT)": weather_info.get('MinT', 'no data'),
                    "最高溫度 (MaxT)": weather_info.get('MaxT', 'no data'),
                    "天氣現象 (Wx)": weather_info.get('Wx', 'no data'),
                    "12小時降雨機率 (PoP12h)": weather_info.get('PoP12h', 'no data')
                }
                
                return weather_data
        
        return {"error": "找不到指定地點的天氣資料"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"網路請求錯誤：{e}"}
    except Exception as e:
        return {"error": f"未知錯誤：{e}"}