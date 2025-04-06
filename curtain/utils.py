import requests

# 네이버지도api 를 통해 주소로 좌표를 가져옴
def get_lat_lng(address):
    client_id = 'baf5z1xz04'          # 발급받은 Client ID로 변경
    client_secret = '0BffxJrPrzJrrT1xTWSEnMMKeORsCZ6Avgq7tKhz'  # 발급받은 Client Secret으로 변경

    url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode'

    params = {'query': address}

    headers = {
        'X-NCP-APIGW-API-KEY-ID': client_id,
        'X-NCP-APIGW-API-KEY': client_secret,
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['meta']['totalCount'] > 0:
            x = data['addresses'][0]['x']  # 경도
            y = data['addresses'][0]['y']  # 위도
            return float(y), float(x)
        else:
            print('주소에 대한 좌표를 찾을 수 없습니다.')
            return None, None
    else:
        print('API 요청 에러:', response.status_code)
        return None, None