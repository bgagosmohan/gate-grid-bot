#!/usr/bin/env python3
"""
Gate.io Grid Trading Bot — Free Edition
自动网格交易，低买高卖赚价差。
Pro版（付费解锁）：多币对并行、回测、Telegram通知、AI信号增强

付款：TRC20-USDT: TQxRpFw8Ae6SfrCHxznGdugUP2ejshT35k
GitHub Sponsors: https://github.com/sponsors/bgagosmohan
"""
import hmac
import hashlib
import json
import time
import requests
import sys
from datetime import datetime

# ========== CONFIG ==========
API_KEY = ""        # 填你的 Gate.io API Key
API_SECRET = ""     # 填你的 Gate.io API Secret
SYMBOL = "SWARMS_USDT"
GRID_COUNT = 10      # 网格层数
GRID_SPREAD = 0.005  # 每层价差 0.5%
ORDER_SIZE = 5       # 每单 USDT 金额
MAX_POSITION = 50    # 最大持仓 USDT
# ============================

BASE = "https://api.gateio.ws/api/v4"

def sign(method, path, query="", body=""):
    t = str(int(time.time()))
    m = hashlib.sha512()
    payload = f"{method}\n{path}\n{query}\n{hashlib.sha512(body.encode()).hexdigest()}\n{t}"
    m.update(payload.encode())
    sign = hmac.new(API_SECRET.encode(), m.digest(), hashlib.sha512).hexdigest()
    return {"KEY": API_KEY, "Timestamp": t, "SIGN": sign}

def api(method, path, params=None):
    url = f"{BASE}{path}"
    headers = sign(method, path, query="")
    headers["Accept"] = "application/json"
    if method == "GET":
        resp = requests.get(url, headers=headers, params=params, timeout=10)
    else:
        headers["Content-Type"] = "application/json"
        resp = requests.post(url, headers=headers, json=params, timeout=10)
    return resp.json() if resp.status_code == 200 else {"error": resp.text}

def get_price(symbol):
    tickers = requests.get(f"{BASE}/spot/tickers", params={"currency_pair": symbol}, timeout=10).json()
    return float(tickers[0]["last"]) if tickers else 0

def get_balance(currency):
    try:
        r = api("GET", f"/spot/accounts/{currency}")
        return float(r.get("available", 0))
    except:
        return 0

def place_order(side, price, size):
    return api("POST", "/spot/orders", {
        "currency_pair": SYMBOL,
        "type": "limit",
        "account": "spot",
        "side": side,
        "amount": str(size),
        "price": str(price),
        "time_in_force": "gtc"
    })

def cancel_all():
    orders = api("GET", "/spot/open_orders", {"currency_pair": SYMBOL, "limit": 100})
    if isinstance(orders, list):
        for o in orders:
            api("DELETE", f"/spot/orders/{o['id']}", {"currency_pair": SYMBOL})

def get_open_orders():
    r = api("GET", "/spot/open_orders", {"currency_pair": SYMBOL, "limit": 100})
    return r if isinstance(r, list) else []

def run_grid():
    if not API_KEY or not API_SECRET:
        print("⚠️ 请先设置 API_KEY 和 API_SECRET")
        print("   Gate.io → 账户 → API管理 → 创建API Key（交易权限）")
        return

    price = get_price(SYMBOL)
    if not price:
        print("❌ 获取价格失败")
        return

    base, quote = SYMBOL.split("_")
    quote_balance = get_balance(quote)
    base_balance = get_balance(base)

    print(f"\n{'='*55}")
    print(f"  🤖 Gate Grid Bot | {SYMBOL} | {datetime.now().strftime('%H:%M:%S')}")
    print(f"  💵 价格: {price} | USDT余额: {quote_balance:.2f} | {base}持仓: {base_balance:.4f}")
    print(f"{'='*55}")

    # 计算网格
    grid_low = price * (1 - GRID_SPREAD * GRID_COUNT / 2)
    grid_high = price * (1 + GRID_SPREAD * GRID_COUNT / 2)
    current_position_value = base_balance * price

    print(f"  📊 网格范围: {grid_low:.6f} ~ {grid_high:.6f}")
    print(f"  📈 当前持仓价值: ${current_position_value:.2f} / 上限 ${MAX_POSITION}")

    # 取消旧单
    cancel_all()

    buy_count = 0
    sell_count = 0

    for i in range(GRID_COUNT):
        level = i - GRID_COUNT // 2
        grid_price = round(price * (1 + level * GRID_SPREAD), 6)

        if grid_price < price and current_position_value < MAX_POSITION:
            # 低于现价 → 挂买单
            r = place_order("buy", grid_price, round(ORDER_SIZE / grid_price, 4))
            if "error" not in r:
                buy_count += 1
        elif grid_price > price and base_balance > 0:
            # 高于现价 → 挂卖单
            sell_size = min(base_balance / (GRID_COUNT // 2), ORDER_SIZE / grid_price)
            if sell_size > 0:
                r = place_order("sell", grid_price, round(sell_size, 4))
                if "error" not in r:
                    sell_count += 1

    print(f"  ✅ 已挂 {buy_count} 买单 + {sell_count} 卖单")

    # 检查成交
    orders = get_open_orders()
    print(f"  📋 当前挂单: {len(orders)} 个")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        print("🔄 循环模式启动 (每30秒)...")
        while True:
            try:
                run_grid()
            except Exception as e:
                print(f"⚠️ 错误: {e}")
            time.sleep(30)
    else:
        run_grid()
