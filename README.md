Để cho biết được trạng thái của job timeout là đã gửi log hay chưa cần có hiện thị trên csdl.
Việc thêm một cột check vào bảng video không thể mô tả rõ ràng các vấn đề của log như là đã timeout bao nhiêu lần nên em đã tạo một bảng mới nhằm mô tả thông tin về log của một job.
Bảng video_timeout_event. 
có các cột 
  id bigint AI PK  
  job_id bigint               id job
  media_id bigint             id media
  resolution varchar(10)       độ phân giải
  time_limit int               thời gian giới hạn
  first_detected_at datetime   Thời gian lần quét đầu phát hiện quá thời gian 
  last_detected_at datetime    Thời gian lần quét cuối phát hiện quá thời gian 
  exceed_minutes int            Quá bao nhiêu phút
  detect_count int              Số lần quét phát hiện quá thời gian
  status varchar(20)             OPEN (Thể hiện job vẫn đang chạy quá thời gian chưa hoàn thành)/CLOSED (Thể hiện Job đã hoàn thành ) 
  created_at datetime           THời gian đầu tiên phát hiện
  updated_at datetime           Thời gian lần cuối cập nhật

  Ý tưởng: Là phát hiện job nào đó quá thời gian liền cho vào bảng này. Sau mỗi lần quét sẽ cập nhật các thông số và trạng thái.
