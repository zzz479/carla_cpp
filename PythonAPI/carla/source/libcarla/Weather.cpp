// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#include <carla/rpc/WeatherParameters.h>

#include <ostream>

namespace carla {

//rpc命名空间，通常用于存放与远程过程调用（RPC）相关的功能和数据类型相关的代码
namespace rpc {

  std::ostream &operator<<(std::ostream &out, const WeatherParameters &weather) {
    out << "WeatherParameters(cloudiness=" << std::to_string(weather.cloudiness)
        << ", precipitation=" << std::to_string(weather.precipitation)
        << ", precipitation_deposits=" << std::to_string(weather.precipitation_deposits)
        << ", wind_intensity=" << std::to_string(weather.wind_intensity)
        << ", sun_azimuth_angle=" << std::to_string(weather.sun_azimuth_angle)
        << ", sun_altitude_angle=" << std::to_string(weather.sun_altitude_angle)
        << ", fog_density=" << std::to_string(weather.fog_density)
        << ", fog_distance=" << std::to_string(weather.fog_distance)
        << ", fog_falloff=" << std::to_string(weather.fog_falloff)
        << ", wetness=" << std::to_string(weather.wetness)
        << ", scattering_intensity=" << std::to_string(weather.scattering_intensity)
        << ", mie_scattering_scale=" << std::to_string(weather.mie_scattering_scale)
        << ", rayleigh_scattering_scale=" << std::to_string(weather.rayleigh_scattering_scale)
        << ", dust_storm=" << std::to_string(weather.dust_storm) << ')';
    return out;//返回输出流对象
  }

} // namespace rpc
} // namespace carla

void export_weather() {//将WeatherParameters相关的类型、类等信息导出到Python环境中
  using namespace boost::python;
  namespace cr = carla::rpc;

  // 使用class_模板在Python环境中定义一个名为WeatherParameters的类，对应于C++中的carla::rpc::WeatherParameters类
  auto cls = class_<cr::WeatherParameters>("WeatherParameters")
     // 定义WeatherParameters类的构造函数，可接受多个默认参数，用于初始化WeatherParameters对象的各个天气参数
     // 参数分别对应不同的天气参数，如cloudiness、precipitation等，每个参数都有默认值，如cloudiness的默认值为0.0f
    // 定义一个构造函数，接受14个float类型的参数，每个参数都有默认值0.0f
.def(init<float, float, float, float, float, float, float, float, float, float, float, float, float, float>(
        (arg("cloudiness")=0.0f,           // 云量
         arg("precipitation")=0.0f,        // 降水量
         arg("precipitation_deposits")=0.0f, // 降水沉积量
         arg("wind_intensity")=0.0f,       // 风力强度
         arg("sun_azimuth_angle")=0.0f,    // 太阳方位角
         arg("sun_altitude_angle")=0.0f,   // 太阳高度角
         arg("fog_density")=0.0f,          // 雾密度
         arg("fog_distance")=0.0f,         // 雾距离
         arg("fog_falloff")=0.0f,          // 雾衰减
         arg("wetness")=0.0f,              // 湿润度
         arg("scattering_intensity")=0.0f, // 散射强度
         arg("mie_scattering_scale")=0.0f, // Mie散射尺度
         arg("rayleigh_scattering_scale")=0.0331f, // Rayleigh散射尺度
         arg("dust_storm")=0.0f)))         // 沙尘暴强度

// 为WeatherParameters类的成员变量定义读写接口
.def_readwrite("cloudiness", &cr::WeatherParameters::cloudiness)              // 云量
.def_readwrite("precipitation", &cr::WeatherParameters::precipitation)        // 降水量
.def_readwrite("precipitation_deposits", &cr::WeatherParameters::precipitation_deposits) // 降水沉积量
.def_readwrite("wind_intensity", &cr::WeatherParameters::wind_intensity)      // 风力强度
.def_readwrite("sun_azimuth_angle", &cr::WeatherParameters::sun_azimuth_angle)// 太阳方位角
.def_readwrite("sun_altitude_angle", &cr::WeatherParameters::sun_altitude_angle) // 太阳高度角
.def_readwrite("fog_density", &cr::WeatherParameters::fog_density)            // 雾密度
.def_readwrite("fog_distance", &cr::WeatherParameters::fog_distance)          // 雾距离
.def_readwrite("fog_falloff", &cr::WeatherParameters::fog_falloff)            // 雾衰减
.def_readwrite("wetness", &cr::WeatherParameters::wetness)                    // 湿润度
.def_readwrite("scattering_intensity", &cr::WeatherParameters::scattering_intensity) // 散射强度
.def_readwrite("mie_scattering_scale", &cr::WeatherParameters::mie_scattering_scale) // Mie散射尺度
.def_readwrite("rayleigh_scattering_scale", &cr::WeatherParameters::rayleigh_scattering_scale) // Rayleigh散射尺度
.def_readwrite("dust_storm", &cr::WeatherParameters::dust_storm)              // 沙尘暴强度

// 为WeatherParameters类定义相等和不相等的比较操作符
.def("__eq__", &cr::WeatherParameters::operator==)
.def("__ne__", &cr::WeatherParameters::operator!=)

// 为WeatherParameters类定义字符串表示方法
// 将WeatherParameters类的字符串表示方法暴露给Python
.def(self_ns::str(self_ns::self))

// 将WeatherParameters类的静态成员作为Python类的属性
cls.attr("Default") = cr::WeatherParameters::Default;          // 默认天气设置
cls.attr("ClearNoon") = cr::WeatherParameters::ClearNoon;      // 晴朗正午
cls.attr("CloudyNoon") = cr::WeatherParameters::CloudyNoon;    // 多云正午
cls.attr("WetNoon") = cr::WeatherParameters::WetNoon;          // 湿润正午
cls.attr("WetCloudyNoon") = cr::WeatherParameters::WetCloudyNoon; // 湿润多云正午
cls.attr("MidRainyNoon") = cr::WeatherParameters::MidRainyNoon; // 中雨正午
cls.attr("HardRainNoon") = cr::WeatherParameters::HardRainNoon; // 大雨正午
cls.attr("SoftRainNoon") = cr::WeatherParameters::SoftRainNoon; // 小雨正午
cls.attr("ClearSunset") = cr::WeatherParameters::ClearSunset;   // 晴朗日落
cls.attr("CloudySunset") = cr::WeatherParameters::CloudySunset; // 多云日落
cls.attr("WetSunset") = cr::WeatherParameters::WetSunset;       // 湿润日落
cls.attr("WetCloudySunset") = cr::WeatherParameters::WetCloudySunset; // 湿润多云日落
cls.attr("MidRainSunset") = cr::WeatherParameters::MidRainSunset; // 中雨日落
cls.attr("HardRainSunset") = cr::WeatherParameters::HardRainSunset; // 大雨日落
cls.attr("SoftRainSunset") = cr::WeatherParameters::SoftRainSunset; // 小雨日落
cls.attr("ClearNight") = cr::WeatherParameters::ClearNight;      // 晴朗夜晚
cls.attr("CloudyNight") = cr::WeatherParameters::CloudyNight;    // 多云夜晚
cls.attr("WetNight") = cr::WeatherParameters::WetNight;          // 湿润夜晚
cls.attr("WetCloudyNight") = cr::WeatherParameters::WetCloudyNight; // 湿润多云夜晚
cls.attr("SoftRainNight") = cr::WeatherParameters::SoftRainNight; // 小雨夜晚
cls.attr("MidRainyNight") = cr::WeatherParameters::MidRainyNight; // 中雨夜晚
cls.attr("HardRainNight") = cr::WeatherParameters::HardRainNight; // 大雨夜晚
cls.attr("DustStorm") = cr::WeatherParameters::DustStorm;         // 沙尘暴
