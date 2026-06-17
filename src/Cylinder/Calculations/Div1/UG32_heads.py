"""ASME BPVC Section VIII, Division 1 -- UG-32 / UG-32(g).

Required thickness and MAWP for formed heads and conical sections under
INTERNAL pressure. These are the closed-form rules from UG-32; they complement
internal_pressure.py (UG-27, cylinders) and the Div 2 modules.

Nomenclature (US customary: in, psi):
    P  internal (design) pressure
    S  maximum allowable stress
    E  joint efficiency (weakest seam in the head)
    D  inside diameter (of the head skirt, or large end for cones)
    L  inside spherical (crown) radius           -- hemispherical, torispherical
    r  inside knuckle radius                      -- torispherical
    h  inside depth of head minus skirt           -- ellipsoidal
    alpha  half-apex angle of the cone, radians   -- conical

All thickness results exclude corrosion allowance; add it separately.
"""
import enum
import math


class HeadType(enum.Enum):
    HEMISPHERICAL = enum.auto()
    ELLIPSOIDAL = enum.auto()
    TORISPHERICAL = enum.auto()
    CONICAL = enum.auto()


# ---- Shape factors ---------------------------------------------------------

# UG-32(c), eq. for K: ellipsoidal head spherical-radius factor.
def K_ellipsoidal(D, h):
    """K = (1/6)[2 + (D / 2h)^2]. For a 2:1 head (h = D/4), K = 1."""
    return (1.0 / 6.0) * (2.0 + (D / (2.0 * h)) ** 2)


# UG-32(d), eq. for M: torispherical head spherical-radius factor.
def M_torispherical(L, r):
    """M = (1/4)[3 + sqrt(L / r)]. Standard F&D (L=D, r=0.06D) gives M ~= 1.77."""
    return 0.25 * (3.0 + math.sqrt(L / r))


# ---- Required thickness ----------------------------------------------------

# UG-32(f): hemispherical head.  t = P L / (2 S E - 0.2 P)
def t_hemispherical(P, S, E, L):
    return (P * L) / (2.0 * S * E - 0.2 * P)


# UG-32(c): ellipsoidal head.  t = P D K / (2 S E - 0.2 P)
def t_ellipsoidal(P, S, E, D, h=None, K=None):
    if K is None:
        K = K_ellipsoidal(D, h if h is not None else D / 4.0)
    return (P * D * K) / (2.0 * S * E - 0.2 * P)


# UG-32(d): torispherical head.  t = P L M / (2 S E - 0.2 P)
def t_torispherical(P, S, E, L, r=None, M=None):
    if M is None:
        M = M_torispherical(L, r if r is not None else 0.06 * L)
    return (P * L * M) / (2.0 * S * E - 0.2 * P)


# UG-32(g): conical section (no transition knuckle).
# t = P D / [2 cos(alpha) (S E - 0.6 P)], D = inside diameter at the point of interest.
def t_conical(P, S, E, D, alpha):
    if alpha >= math.pi / 6.0:  # 30 deg; UG-32(g) limits semi-apex angle to <= 30
        raise ValueError("UG-32(g) requires the cone half-apex angle <= 30 deg; "
                         "use Appendix 1-5 (toriconical / reinforcement) instead.")
    return (P * D) / (2.0 * math.cos(alpha) * (S * E - 0.6 * P))


# ---- MAWP (maximum allowable working pressure) at a given thickness --------

def P_hemispherical(S, E, t, L):
    return (2.0 * S * E * t) / (L + 0.2 * t)


def P_ellipsoidal(S, E, t, D, h=None, K=None):
    if K is None:
        K = K_ellipsoidal(D, h if h is not None else D / 4.0)
    return (2.0 * S * E * t) / (K * D + 0.2 * t)


def P_torispherical(S, E, t, L, r=None, M=None):
    if M is None:
        M = M_torispherical(L, r if r is not None else 0.06 * L)
    return (2.0 * S * E * t) / (M * L + 0.2 * t)


def P_conical(S, E, t, D, alpha):
    c = math.cos(alpha)
    return (2.0 * S * E * t * c) / (D + 1.2 * t * c)


# ---- Dispatch helpers ------------------------------------------------------

def required_thickness(head_type: HeadType, P, S, E, *, D=None, L=None, r=None,
                       h=None, K=None, M=None, alpha=None):
    """Required thickness for the given head type. Pass only the geometry the
    head needs (see each t_* function). Returns thickness in inches."""
    if head_type == HeadType.HEMISPHERICAL:
        return t_hemispherical(P, S, E, L)
    if head_type == HeadType.ELLIPSOIDAL:
        return t_ellipsoidal(P, S, E, D, h=h, K=K)
    if head_type == HeadType.TORISPHERICAL:
        return t_torispherical(P, S, E, L, r=r, M=M)
    if head_type == HeadType.CONICAL:
        return t_conical(P, S, E, D, alpha)
    raise ValueError("Unknown head type %r" % head_type)


if __name__ == "__main__":
    # 2:1 ellipsoidal head, P=100 psi, S=20000 psi, E=1.0, D=48 in
    print("2:1 ellipsoidal t =", t_ellipsoidal(100.0, 20000.0, 1.0, 48.0))
    # hemispherical, L=24 in
    print("hemispherical  t =", t_hemispherical(100.0, 20000.0, 1.0, 24.0))
    # standard F&D torispherical, L=48, r=0.06*48
    print("torispherical  t =", t_torispherical(100.0, 20000.0, 1.0, 48.0))
