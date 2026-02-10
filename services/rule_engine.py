from datetime import datetime, timezone
from config.settings import TIME_LIMIT_BY_RESOLUTION, DEFAULT_LIMIT

#ánh xạ các độ phân giải không phổ biến như 824 về chuẩn gần nhất là 720
def map_resolution(height: int) -> str:
    standards = [720, 1080, 1440, 2160]
    closest = min(standards, key=lambda s:abs(s - height))
    return f"{closest}p"

def get_time_limit(resolution: str) -> int:
    return TIME_LIMIT_BY_RESOLUTION.get(resolution, DEFAULT_LIMIT)

def calc_runtime(start_time):
    # nếu startime là dạng naive thì chuyển sang dạng aware
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo = timezone.utc)

    #lấy dạng aware của thời gian hiên tại
    now = datetime.now(timezone.utc)
    delta = now - start_time
    # trả về số phút chênh lệch làm tròn sau ép kiểu
    return int(delta.total_seconds()/60)

