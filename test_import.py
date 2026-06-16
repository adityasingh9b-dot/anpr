import cpp_ingestion
import cv2

if cpp_ingestion.initialize_camera():
    print("Camera running... Press 'q' to stop.")
    while True:
        frame = cpp_ingestion.get_processed_frame()
        if frame is not None and frame.size > 0:
            cv2.imshow("Live Feed", frame)
            
            # 1ms ka wait aur 'q' press karne par exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()
else:
    print("Camera init failed!")
