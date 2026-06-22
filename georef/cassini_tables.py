"""Cassini-Soldner conversion via NLIMS log tables."""
from __future__ import annotations

from math import cos, log10, pi, sin, tan

from fayvadgeo.survey_math import dec_deg


class CassTable:
    """Traditional log-table Cassini ↔ geographic conversion."""

    def get_index(self, val, arr):
        for i in range(len(arr)):
            if arr[i] > val:
                break
        return i - 1

    @staticmethod
    def _aspect(val):
        return -1 if val < 0 else 1

    def get_diff(self, arr, idx):
        if 0 < idx < len(arr):
            return arr[idx + 1] - arr[idx]
        if idx <= 0:
            return arr[1] - arr[0]
        return arr[len(arr) - 1] - arr[len(arr) - 2]

    def generate_tables(self):
        phi = []
        ph = []
        rho = []
        nu = []
        rhonu2 = []

        for ang in range(6):
            for j in range(6):
                mins = j * 10
                phi.append([ang, mins])
                ph.append(dec_deg(ang, mins))
                rho.append(0)
                nu.append(0)
                rhonu2.append(0)

        roffset = 2.003
        noffset = 2.006
        rnoffset = 0.3749

        r = [
            3115, 3116, 3117, 3119, 3121, 3125, 3129, 3134, 3139, 3145, 3153, 3160,
            3169, 3178, 3188, 3199, 3211, 3223, 3236, 3250, 3265, 3280, 3296, 3313,
            3330, 3349, 3368, 3387, 3408, 3429, 3451,
        ]
        n = [
            2683, 2683, 2684, 2684, 2685, 2686, 2688, 2689, 2691, 2693, 2696, 2698,
            2701, 2704, 2707, 2711, 2715, 2719, 2723, 2728, 2733, 2738, 2743, 2749,
            2755, 2761, 2767, 2774, 2781, 2788, 2795,
        ]
        mer = [
            0.0, 60459.2, 120918.5, 181377.8, 241837.1, 302296.5, 362755.9, 425215.3,
            483674.9, 544154.5, 604594.2, 665054.0, 725514.0, 785974.1, 846434.5,
            906894.6, 967355.1, 1027815.8, 1088276.6, 1148737.6, 1209198.8, 1269660.2,
            1330121.9, 1390583.8, 1451045.9, 1511508.3, 1571970.9, 1632433.8,
            1692897.0, 1753360.5, 1813824.2,
        ]
        rn = [
            65, 65, 65, 65, 64, 64, 63, 63, 62, 61, 60, 59, 58, 57, 55, 54, 52, 51,
            49, 47, 45, 43, 41, 39, 36, 34, 31, 29, 26, 23, 20,
        ]

        for i in range(len(r)):
            rho[i] = roffset + r[i] * 10e-8
            nu[i] = noffset + n[i] * 10e-8
            rhonu2[i] = -10 + rnoffset + rn[i] * 10e-7
        return phi, ph, rho, nu, mer, rhonu2

    def compute_geog(self, x: float, y: float, central_meridian: float) -> tuple[float, float]:
        asp_y = self._aspect(y)
        y_abs = abs(y)
        asp_x = self._aspect(x)
        x_abs = abs(x)
        phi, ph, rho, nu, mer, _rhonu2 = self.generate_tables()
        i = self.get_index(y_abs, mer)
        diff_y = y_abs - mer[i]
        diff = self.get_diff(mer, i)
        fract = diff_y / diff if diff > 0 else diff_y / (mer[1] - mer[0])
        del_ang = float(f'{fract * 600:10.4f}')
        angle = phi[i][0] + phi[i][1] / 60.0 + del_ang / 3600.0
        ang = angle / 180.0 * pi
        logtan = log10(tan(ang))
        logx = log10(x_abs)
        xlog2 = logx * 2
        logsin1sec = log10(sin(1.0 / 3600 * pi / 180.0))
        n_val = nu[i] + fract * self.get_diff(nu, i)
        r_val = rho[i] + fract * self.get_diff(rho, i)
        rnu = -(n_val + r_val - logsin1sec + log10(2.0))
        logn = xlog2 + logtan + rnu
        nn = 10 ** logn
        lat = (angle - nn / 3600.0) * asp_y
        logsec = log10(1.0 / cos(angle / 180.0 * pi))
        logdh = logx + logsec - n_val
        dh = 10 ** logdh
        lon = central_meridian + dh / 3600.0 * asp_x
        return lon, lat

    def compute_cass(self, lon: float, lat: float, central_meridian: float) -> tuple[float, float]:
        phi, ph, rho, nu, mer, _rhonu2 = self.generate_tables()
        asp_y = self._aspect(lat)
        lt = abs(lat)
        i = 0 if lt < 1e-10 else self.get_index(lt, ph)
        if lt < 1e-10:
            lt = 1e-10
        yp = mer[i]
        del_ang = lt - ph[i]
        diff = self.get_diff(mer, i)
        if i > 0:
            dy = del_ang * 3600.0 * diff / 600.0
        else:
            dy = del_ang * 3600.0 * (mer[1] - mer[0]) / 600.0
        fract = dy / diff
        dh = (lon - central_meridian) * 3600.0
        asp_x = self._aspect(dh)
        dh = abs(dh)
        if dh < 1e-10:
            dh = 1e-10
        logdh = log10(dh)
        logcos = log10(cos(lt * pi / 180.0))
        logcos2 = 2.0 * logcos
        logdh2 = logdh * 2
        logtan = log10(tan(lt * pi / 180.0))
        n_val = nu[i] + self.get_diff(nu, i) * fract
        loghalf = log10(0.5)
        logsin = log10(sin(pi / (3600.0 * 180.0)))
        logn = logdh2 + logcos2 + logtan + logsin + loghalf + n_val
        y = (yp + dy + 10 ** logn) * asp_y
        logx = logdh + logcos + n_val
        x = 10 ** logx * asp_x
        return x, y
