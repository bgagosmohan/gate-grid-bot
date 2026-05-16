# 🤖 Gate Grid Bot — 自动网格交易机器人

**FREE 开源版** — Gate.io 现货网格交易，低买高卖自动赚价差。

## Pro 版功能（5 USDT 解锁）
- 🔥 多币对并行（同时跑 5-10 个交易对）
- 📊 历史回测引擎
- 📱 Telegram 实时推送
- 🧠 AI 信号增强（自动选币 + 调参）
- 💰 止盈止损保护

**付款后联系 Telegram 获取 Pro 版。**

## 快速开始

```bash
git clone https://github.com/bgagosmohan/gate-grid-bot.git
cd gate-grid-bot
pip install -r requirements.txt
```

1. 去 [Gate.io API 管理](https://www.gate.io/myaccount/api_key_management) 创建 Key
2. 编辑 `bot.py`，填入 `API_KEY` 和 `API_SECRET`
3. 运行：

```bash
python bot.py           # 单次执行
python bot.py --loop    # 循环模式(每30秒)
```

## 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `SYMBOL` | 交易对 | SWARMS_USDT |
| `GRID_COUNT` | 网格层数 | 10 |
| `GRID_SPREAD` | 每层价差% | 0.005 (0.5%) |
| `ORDER_SIZE` | 每单USDT | 5 |
| `MAX_POSITION` | 最大持仓USDT | 50 |

## ⚠️ 风险提示

网格交易不是稳赚。单边行情会套牢。仅投入你能承受损失的资金。

## 💰 支持作者

- **TRC20-USDT**: `TQxRpFw8Ae6SfrCHxznGdugUP2ejshT35k`
- **GitHub Sponsors**: [赞助我](https://github.com/sponsors/bgagosmohan)
- **Pro版购买**: 转 5 USDT 到上面地址，Telegram 联系获取

## License

MIT — 随便用，亏了别找我。
