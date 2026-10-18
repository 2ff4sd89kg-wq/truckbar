"""Reads ATS/ETS2 live telemetry from the RenCloud scs-telemetry plugin.

The plugin (bin/win_x64/plugins/scs-telemetry.dll) publishes one struct in shared
memory named Local\\SCSTelemetry. This mirrors scsTelemetryMap_t from the plugin's
scs-telemetry-common.hpp (PLUGIN_REVID 12). Only the parts the bar uses are named;
the rest is padding with the same size, so every offset matches the header.
OpenFileMapping is used rather than mmap so we never create the mapping ourselves
when the game is not running.
"""
import ctypes as C
from ctypes import wintypes as W

PLUGIN_REVISION = 12   # the struct below matches this revision of the plugin
MMF_NAME = "Local\\SCSTelemetry"
MMF_SIZE = 32 * 1024
S = 64  # stringsize


class Telemetry(C.Structure):
    _fields_ = [
        # zone 1 @0
        ("sdkActive", C.c_bool), ("_p1", C.c_char * 3),
        ("paused", C.c_bool), ("_p2", C.c_char * 3),
        ("time", C.c_uint64), ("simulatedTime", C.c_uint64),
        ("renderTime", C.c_uint64), ("multiplayerTimeOffset", C.c_int64),
        # zone 2 @40 - unsigned ints
        ("plugin_revision", C.c_uint), ("version_major", C.c_uint), ("version_minor", C.c_uint),
        ("game", C.c_uint), ("tel_major", C.c_uint), ("tel_minor", C.c_uint),
        ("time_abs", C.c_uint),
        ("gears", C.c_uint), ("gears_reverse", C.c_uint), ("retarderStepCount", C.c_uint),
        ("truckWheelCount", C.c_uint), ("selectorCount", C.c_uint), ("time_abs_delivery", C.c_uint),
        ("maxTrailerCount", C.c_uint), ("unitCount", C.c_uint), ("plannedDistanceKm", C.c_uint),
        ("shifterSlot", C.c_uint), ("retarderBrake", C.c_uint),
        ("lightsAuxFront", C.c_uint), ("lightsAuxRoof", C.c_uint),
        ("truck_wheelSubstance", C.c_uint * 16), ("hshifterPosition", C.c_uint * 32),
        ("hshifterBitmask", C.c_uint * 32),
        ("jobDeliveredDeliveryTime", C.c_uint), ("jobStartingTime", C.c_uint), ("jobFinishedTime", C.c_uint),
        ("_buffer_ui", C.c_char * 48),
        # zone 3 @500 - ints
        ("restStop", C.c_int), ("gear", C.c_int), ("gearDashboard", C.c_int),
        ("hshifterResulting", C.c_int * 32), ("jobDeliveredEarnedXp", C.c_int),
        ("_buffer_i", C.c_char * 56),
        # zone 4 @700 - floats
        ("scale", C.c_float),
        ("fuelCapacity", C.c_float), ("fuelWarningFactor", C.c_float),
        ("adblueCapacity", C.c_float), ("adblueWarningFactor", C.c_float),
        ("airPressureWarningLevel", C.c_float), ("airPressureEmergencyLevel", C.c_float),
        ("oilPressureWarningLevel", C.c_float), ("waterTemperatureWarningLevel", C.c_float),
        ("batteryVoltageWarningLevel", C.c_float), ("engineRpmMax", C.c_float),
        ("gearDifferential", C.c_float), ("cargoMass", C.c_float),
        ("truckWheelRadius", C.c_float * 16), ("gearRatiosForward", C.c_float * 24),
        ("gearRatiosReverse", C.c_float * 8), ("unitMass", C.c_float),
        ("speed", C.c_float), ("engineRpm", C.c_float),
        ("userSteer", C.c_float), ("userThrottle", C.c_float), ("userBrake", C.c_float), ("userClutch", C.c_float),
        ("gameSteer", C.c_float), ("gameThrottle", C.c_float), ("gameBrake", C.c_float), ("gameClutch", C.c_float),
        ("cruiseControlSpeed", C.c_float), ("airPressure", C.c_float), ("brakeTemperature", C.c_float),
        ("fuel", C.c_float), ("fuelAvgConsumption", C.c_float), ("fuelRange", C.c_float),
        ("adblue", C.c_float), ("oilPressure", C.c_float), ("oilTemperature", C.c_float),
        ("waterTemperature", C.c_float), ("batteryVoltage", C.c_float), ("lightsDashboard", C.c_float),
        ("wearEngine", C.c_float), ("wearTransmission", C.c_float), ("wearCabin", C.c_float),
        ("wearChassis", C.c_float), ("wearWheels", C.c_float), ("truckOdometer", C.c_float),
        ("routeDistance", C.c_float), ("routeTime", C.c_float), ("speedLimit", C.c_float),
        ("_wheel_f", C.c_float * (16 * 6)),
        ("jobDeliveredCargoDamage", C.c_float), ("jobDeliveredDistanceKm", C.c_float),
        ("refuelAmount", C.c_float), ("cargoDamage", C.c_float),
        ("_buffer_f", C.c_char * 28),
        # zone 5 @1500 - bools
        ("_cfg_wheels_b", C.c_bool * 64), ("isCargoLoaded", C.c_bool), ("specialJob", C.c_bool),
        ("parkBrake", C.c_bool), ("motorBrake", C.c_bool),
        ("airPressureWarning", C.c_bool), ("airPressureEmergency", C.c_bool),
        ("fuelWarning", C.c_bool), ("adblueWarning", C.c_bool),
        ("oilPressureWarning", C.c_bool), ("waterTemperatureWarning", C.c_bool),
        ("batteryVoltageWarning", C.c_bool), ("electricEnabled", C.c_bool), ("engineEnabled", C.c_bool),
        ("wipers", C.c_bool), ("blinkerLeftActive", C.c_bool), ("blinkerRightActive", C.c_bool),
        ("blinkerLeftOn", C.c_bool), ("blinkerRightOn", C.c_bool),
        ("lightsParking", C.c_bool), ("lightsBeamLow", C.c_bool), ("lightsBeamHigh", C.c_bool),
        ("lightsBeacon", C.c_bool), ("lightsBrake", C.c_bool), ("lightsReverse", C.c_bool),
        ("lightsHazard", C.c_bool), ("cruiseControl", C.c_bool),
        ("truck_wheelOnGround", C.c_bool * 16), ("shifterToggle", C.c_bool * 2),
        ("differentialLock", C.c_bool), ("liftAxle", C.c_bool), ("liftAxleIndicator", C.c_bool),
        ("trailerLiftAxle", C.c_bool), ("trailerLiftAxleIndicator", C.c_bool),
        ("jobDeliveredAutoparkUsed", C.c_bool), ("jobDeliveredAutoloadUsed", C.c_bool),
        ("_buffer_b", C.c_char * 25),
        # zones 6-7 @1640 (fvector, fplacement) - not used
        ("_z6_7", C.c_char * (2200 - 1640)),
        # zone 8 @2200 - truck world placement. heading is 0..1, counter-clockwise
        # from north (0.25 = west), so compass bearing = (1 - heading) * 360
        ("coordinateX", C.c_double), ("coordinateY", C.c_double), ("coordinateZ", C.c_double),
        ("heading", C.c_double), ("pitch", C.c_double), ("roll", C.c_double),
        ("_buffer_dp", C.c_char * 52),
        # zone 9 @2300 - strings
        ("truckBrandId", C.c_char * S), ("truckBrand", C.c_char * S), ("truckId", C.c_char * S),
        ("truckName", C.c_char * S), ("cargoId", C.c_char * S), ("cargo", C.c_char * S),
        ("cityDstId", C.c_char * S), ("cityDst", C.c_char * S),
        ("compDstId", C.c_char * S), ("compDst", C.c_char * S),
        ("citySrcId", C.c_char * S), ("citySrc", C.c_char * S),
        ("compSrcId", C.c_char * S), ("compSrc", C.c_char * S),
        ("shifterType", C.c_char * 16),
        ("_z9_rest", C.c_char * (4000 - 2300 - 14 * S - 16)),
        # zone 10 @4000
        ("jobIncome", C.c_uint64), ("_buffer_ull", C.c_char * 192),
        # zone 11 @4200
        ("_z11", C.c_char * 100),
        # zone 12 @4300
        ("onJob", C.c_bool), ("jobFinished", C.c_bool), ("jobCancelled", C.c_bool),
        ("jobDelivered", C.c_bool), ("fined", C.c_bool), ("tollgate", C.c_bool),
        ("ferry", C.c_bool), ("train", C.c_bool), ("refuel", C.c_bool), ("refuelPayed", C.c_bool),
        ("_buffer_special", C.c_char * 90),
    ]


# The header marks where every zone starts; if any of these fail, the struct above is wrong.
_ZONES = {"plugin_revision": 40, "restStop": 500, "scale": 700, "speed": 948,
          "_cfg_wheels_b": 1500, "parkBrake": 1566, "_z6_7": 1640, "coordinateX": 2200, "truckBrandId": 2300,
          "jobIncome": 4000, "_z11": 4200, "onJob": 4300}
for _name, _off in _ZONES.items():
    assert getattr(Telemetry, _name).offset == _off, (_name, getattr(Telemetry, _name).offset, _off)
assert C.sizeof(Telemetry) == 4400, C.sizeof(Telemetry)

_k32 = C.WinDLL("kernel32", use_last_error=True)
_k32.OpenFileMappingW.restype = W.HANDLE
_k32.OpenFileMappingW.argtypes = [W.DWORD, W.BOOL, W.LPCWSTR]
_k32.MapViewOfFile.restype = C.c_void_p
_k32.MapViewOfFile.argtypes = [W.HANDLE, W.DWORD, W.DWORD, W.DWORD, C.c_size_t]
_k32.UnmapViewOfFile.argtypes = [C.c_void_p]
_k32.CloseHandle.argtypes = [W.HANDLE]
FILE_MAP_READ = 0x0004


class Reader:
    """Opens the mapping when it exists; read() returns a copy or None."""

    def __init__(self):
        self._h = None
        self._view = None

    def _open(self):
        h = _k32.OpenFileMappingW(FILE_MAP_READ, False, MMF_NAME)
        if not h:
            return False
        v = _k32.MapViewOfFile(h, FILE_MAP_READ, 0, 0, C.sizeof(Telemetry))
        if not v:
            _k32.CloseHandle(h)
            return False
        self._h, self._view = h, v
        return True

    def close(self):
        if self._view:
            _k32.UnmapViewOfFile(self._view)
        if self._h:
            _k32.CloseHandle(self._h)
        self._h = self._view = None

    def read(self):
        if not self._view and not self._open():
            return None
        return Telemetry.from_buffer_copy(C.string_at(self._view, C.sizeof(Telemetry)))


def text(field):
    return field.decode("utf-8", "replace") if isinstance(field, bytes) else str(field)
