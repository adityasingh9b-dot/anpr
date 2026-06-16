#include <opencv2/opencv.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

cv::VideoCapture cap;
cv::Mat frame, gray, resized;

bool initialize_camera() {
    if (cap.isOpened()) return true;
    cap.open(0, cv::CAP_V4L2);
    // Camera setting: Performance optimization
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    return cap.isOpened();
}

std::string verify_plate(std::string plate_number) {

    try {

        py::gil_scoped_acquire acquire;

        

        // Python path setup

        py::module_ sys = py::module_::import("sys");

        sys.attr("path").attr("append")("/home/aditya/Desktop/anpr");



        // Simple import ab kaam karega

        py::module_ db_mod = py::module_::import("database.db_manager");

        py::object check_func = db_mod.attr("check_vehicle_status");

        py::dict result = check_func(plate_number).cast<py::dict>();

        return result["status"].cast<std::string>();

    } catch (const std::exception& e) {

        return "ERROR: " + std::string(e.what());

    }

}

py::array_t<unsigned char> get_processed_frame() {
    if (!cap.isOpened() || !cap.read(frame))
        return py::array_t<unsigned char>();

    cv::resize(frame, resized, cv::Size(640, 480));

    // Fix: Shape define karo (rows, cols, 3 channels)
    auto result = py::array_t<unsigned char>({resized.rows, resized.cols, 3});
    
    // Copy data
    std::memcpy(result.mutable_data(), resized.data, resized.total() * resized.elemSize());
    
    return result;
}

PYBIND11_MODULE(cpp_ingestion, m) {
    m.def("initialize_camera", &initialize_camera);
    m.def("get_processed_frame", &get_processed_frame);
    m.def("verify_plate", &verify_plate);
}
