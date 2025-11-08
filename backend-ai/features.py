# features.py
import numpy as np
from math import atan2, cos, sin

# 21 điểm theo MediaPipe: 0=wrist; thumb:1..4; index:5..8; middle:9..12; ring:13..16; pinky:17..20
IDX = {"wrist":0,"thumb":[1,2,3,4],"index":[5,6,7,8],"middle":[9,10,11,12],"ring":[13,14,15,16],"pinky":[17,18,19,20]}

def palm_size(kps):
    w = kps[0]
    mcps = [kps[5], kps[9], kps[13], kps[17]]
    return float(np.mean([np.linalg.norm(m-w) for m in mcps]) + 1e-6)

def angle(a,b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na<1e-6 or nb<1e-6: return 180.0
    v = np.clip(np.dot(a,b)/(na*nb), -1.0, 1.0)
    return float(np.degrees(np.arccos(v)))

def normalize_xy(kps):
    """Tịnh tiến về cổ tay, scale theo palm_size, xoay để vector wrist->middle_MCP dọc lên."""
    k = kps.copy().astype(np.float32)
    w = k[0]
    k -= w
    ps = palm_size(k)
    k /= ps
    # hướng trục xoay: wrist -> middle MCP (9)
    ref = k[9]
    theta = -atan2(ref[1], ref[0])  # xoay sao cho ref nằm dọc trục x
    c, s = cos(theta), sin(theta)
    R = np.array([[c,-s],[s,c]], dtype=np.float32)
    k = (R @ k.T).T
    return k  # (21,2)

def finger_metrics(kps, fidx):
    mcp,pip,dip,tip = kps[fidx[0]], kps[fidx[1]], kps[fidx[2]], kps[fidx[3]]
    L = np.linalg.norm(tip-mcp)             # (đã chuẩn hoá trong normalize_xy)
    A = angle(pip-mcp, dip-pip)             # nhỏ → thẳng
    return L, A

def pairwise_features(k):
    # khoảng cách/tỷ lệ hay dùng
    def d(i,j): return float(np.linalg.norm(k[i]-k[j]))
    feats = []
    feats += [d(8,12), d(4,8), d(4,12), d(8,0), d(12,0)]  # index-mid gap, thumb-index/mid, index-wrist, mid-wrist
    feats = [f for f in feats]
    return feats

def extract_features(kps_xy):
    """
    Input: kps_xy (21,2) (pixel). Output: 1D vector ~ 21*2 raw + 5*2 metrics + pairwise.
    """
    k = normalize_xy(kps_xy)             # (21,2) đã chuẩn hoá
    raw = k.reshape(-1)                  # 42 dims

    # độ dài + góc tại PIP của 5 ngón
    L_t, A_t = finger_metrics(k, IDX["thumb"])
    L_i, A_i = finger_metrics(k, IDX["index"])
    L_m, A_m = finger_metrics(k, IDX["middle"])
    L_r, A_r = finger_metrics(k, IDX["ring"])
    L_p, A_p = finger_metrics(k, IDX["pinky"])
    metrics = np.array([L_t,A_t,L_i,A_i,L_m,A_m,L_r,A_r,L_p,A_p], dtype=np.float32)

    pw = np.array(pairwise_features(k), dtype=np.float32)

    return np.concatenate([raw, metrics, pw], axis=0)   # ~42 + 10 + 5 = 57 dims

