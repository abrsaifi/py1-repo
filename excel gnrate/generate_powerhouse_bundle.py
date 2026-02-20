import xlsxwriter

OUT_FILE = "Excel_Powerhouse_Master.xlsx"

N_TRADE_ROWS = 5000
N_PRICE_ROWS = 1000
N_DAYS = 366

def fmt(wb):
    return {
        "title": wb.add_format({"bold": True, "font_size": 14}),
        "h": wb.add_format({"bold": True, "bg_color": "#111827", "font_color": "white", "border": 1}),
        "cell": wb.add_format({"border": 1}),
        "input": wb.add_format({"border": 1, "bg_color": "#FFF2CC"}),
        "calc": wb.add_format({"border": 1, "bg_color": "#F3F4F6"}),
        "note": wb.add_format({"italic": True, "font_color": "#374151"}),
        "dt": wb.add_format({"border": 1, "num_format": "yyyy-mm-dd hh:mm"}),
        "date": wb.add_format({"border": 1, "num_format": "yyyy-mm-dd"}),
        "money": wb.add_format({"border": 1, "num_format": "$#,##0.00"}),
        "pct": wb.add_format({"border": 1, "num_format": "0.00%"}),
        "num": wb.add_format({"border": 1, "num_format": "0.########"}),
        "kpi": wb.add_format({"bold": True, "font_size": 12, "bg_color": "#F3F4F6", "border": 1}),
    }

def set_cols(ws, widths):
    for col, w in enumerate(widths):
        ws.set_column(col, col, w)

def build():
    wb = xlsxwriter.Workbook(OUT_FILE)
    f = fmt(wb)

    sh_settings = wb.add_worksheet("Settings")
    sh_trades   = wb.add_worksheet("Trades")
    sh_symbols  = wb.add_worksheet("Symbols")
    sh_prices   = wb.add_worksheet("Prices")
    sh_equity   = wb.add_worksheet("Equity_Curve")
    sh_dd       = wb.add_worksheet("Drawdown")
    sh_fifo     = wb.add_worksheet("FIFO_Lots")
    sh_real     = wb.add_worksheet("Realized_PnL_FIFO")
    sh_dash     = wb.add_worksheet("Dashboard")
    sh_risk     = wb.add_worksheet("Scenarios_Risk")
    sh_audit    = wb.add_worksheet("Audit_Checks")
    sh_help     = wb.add_worksheet("Help")

    # ---------------- Settings ----------------
    sh_settings.write("A1", "Excel Powerhouse Master (Stocks + Crypto)", f["title"])
    sh_settings.write("A3", "Core settings", f["h"])
    sh_settings.write("A4", "Base currency", f["cell"]);        sh_settings.write("B4", "USD", f["input"])
    sh_settings.write("A5", "Price source", f["cell"]);        sh_settings.write("B5", "Binance", f["input"])
    sh_settings.write("A6", "Production mode", f["cell"]);     sh_settings.write("B6", "OFF", f["input"])
    sh_settings.write("A7", "Equity start date", f["cell"]);   sh_settings.write("B7", "2026-01-01", f["input"])
    sh_settings.write("A8", "Equity end date", f["cell"]);     sh_settings.write("B8", "2026-12-31", f["input"])
    sh_settings.write("A9", "Include fees in P/L", f["cell"]); sh_settings.write("B9", "YES", f["input"])
    sh_settings.write("A10", "Initial cash", f["cell"]);       sh_settings.write_number("B10", 0, f["input"])

    sh_settings.data_validation("B5", {"validate":"list", "source":["Binance","CoinGecko","Manual"]})
    sh_settings.data_validation("B6", {"validate":"list", "source":["ON","OFF"]})
    sh_settings.data_validation("B9", {"validate":"list", "source":["YES","NO"]})
    set_cols(sh_settings, [22, 18, 14, 14])

    wb.define_name("PriceSource", "=Settings!$B$5")
    wb.define_name("ProductionMode", "=Settings!$B$6")
    wb.define_name("StartDate", "=Settings!$B$7")
    wb.define_name("EndDate", "=Settings!$B$8")
    wb.define_name("IncludeFees", "=Settings!$B$9")
    wb.define_name("InitialCash", "=Settings!$B$10")

    # ---------------- Symbols ----------------
    sh_symbols.write("A1", "Symbols master (enable only what you trade)", f["title"])
    headers = ["Symbol","AssetType","Enabled"]
    for j,h in enumerate(headers):
        sh_symbols.write(2, j, h, f["h"])
    starter = [("AAPL","Stock","TRUE"),("MSFT","Stock","FALSE"),("BTC","Crypto","TRUE"),("ETH","Crypto","TRUE")]
    for i, row in enumerate(starter, start=3):
        sh_symbols.write(i, 0, row[0], f["input"])
        sh_symbols.write(i, 1, row[1], f["input"])
        sh_symbols.write(i, 2, row[2], f["input"])
    sh_symbols.data_validation(3,1, N_PRICE_ROWS+2,1, {"validate":"list","source":["Stock","Crypto"]})
    sh_symbols.data_validation(3,2, N_PRICE_ROWS+2,2, {"validate":"list","source":["TRUE","FALSE"]})
    set_cols(sh_symbols, [12, 10, 10])

    # ---------------- Prices ----------------
    sh_prices.write("A1", "Prices (ActivePrice auto-switches by Settings)", f["title"])
    p_headers = ["Symbol","BinancePrice","CoinGeckoPrice","ManualPrice","LastUpdated","ActivePrice","SourceUsed","Enabled?"]
    for j,h in enumerate(p_headers):
        sh_prices.write(2, j, h, f["h"])

    for r in range(3, 3 + N_PRICE_ROWS):
        excel_r = r + 1
        sh_prices.write_formula(r, 0, f'=IF(Symbols!A{excel_r}<>"",Symbols!A{excel_r},"")', f["calc"])
        sh_prices.write_blank(r, 1, None, f["input"])
        sh_prices.write_blank(r, 2, None, f["input"])
        sh_prices.write_blank(r, 3, None, f["input"])
        sh_prices.write_formula(r, 4, f'=IF(A{excel_r}<>"",NOW(),"")', f["calc"])
        sh_prices.write_formula(
            r, 5,
            f'=IF(PriceSource="Binance",B{excel_r},IF(PriceSource="CoinGecko",C{excel_r},D{excel_r}))',
            f["calc"]
        )
        sh_prices.write_formula(r, 6, "=PriceSource", f["calc"])
        sh_prices.write_formula(r, 7, f'=IF(Symbols!C{excel_r}<>"",Symbols!C{excel_r},"")', f["calc"])

    set_cols(sh_prices, [12, 12, 14, 12, 20, 12, 12, 10])

    wb.define_name("Prices_Symbol", "=Prices!$A$4:$A$1003")
    wb.define_name("Prices_Active", "=Prices!$F$4:$F$1003")

    # ---------------- Trades ----------------
    sh_trades.write("A1", "Trades (inputs) — helper columns compute cashflow", f["title"])
    t_headers = [
        "TradeID","Timestamp","AssetType","Symbol","Side","Quantity","Price","Fees","FeesCurrency",
        "SignedQty","GrossValue","FeeValue_Base","NetCashFlow"
    ]
    for j,h in enumerate(t_headers):
        sh_trades.write(2, j, h, f["h"])

    sh_trades.data_validation(3,2, 2+N_TRADE_ROWS,2, {"validate":"list","source":["Stock","Crypto"]})
    sh_trades.data_validation(3,4, 2+N_TRADE_ROWS,4, {"validate":"list","source":["BUY","SELL"]})
    sh_trades.data_validation(3,8, 2+N_TRADE_ROWS,8, {"validate":"list","source":["USD","USDT","INR"]})

    for r in range(3, 3 + N_TRADE_ROWS):
        excel_r = r + 1
        for c in range(0, 9):
            sh_trades.write_blank(r, c, None, f["input"])
        sh_trades.write_formula(r, 9,  f'=IF(E{excel_r}="BUY",F{excel_r},-F{excel_r})', f["calc"])
        sh_trades.write_formula(r, 10, f'=F{excel_r}*G{excel_r}', f["calc"])
        sh_trades.write_formula(r, 11, f'=H{excel_r}', f["calc"])
        sh_trades.write_formula(r, 12, f'=IF(E{excel_r}="BUY",-(K{excel_r}+L{excel_r}),(K{excel_r}-L{excel_r}))', f["calc"])

    sh_trades.freeze_panes(3, 0)
    set_cols(sh_trades, [10,20,10,10,8,10,10,10,12,10,12,14,12])
    sh_trades.set_column(1,1,20,f["dt"])
    sh_trades.set_column(5,5,10,f["num"])
    sh_trades.set_column(6,7,10,f["money"])

    # ---------------- Equity curve + drawdown ----------------
    sh_equity.write("A1", "Equity curve + true drawdown (daily)", f["title"])
    e_headers = ["Date","Equity","PeakEquity","Drawdown","Drawdown%","Cash","PositionsValue"]
    for j,h in enumerate(e_headers):
        sh_equity.write(2, j, h, f["h"])

    for i in range(N_DAYS):
        r = 3 + i
        excel_r = r + 1

        sh_equity.write_formula(r, 0, "=DATEVALUE(StartDate)" if i == 0 else f"=A{excel_r-1}+1", f["date"])

        sh_equity.write_formula(
            r, 5,
            f'=InitialCash + SUMIFS(Trades!$M$4:$M${3+N_TRADE_ROWS}, Trades!$B$4:$B${3+N_TRADE_ROWS}, "<="&A{excel_r}+1)',
            f["calc"]
        )

        # Requires Microsoft 365 (MAP/LET)
        sh_equity.write_formula(
            r, 6,
            f'=LET(sym,Prices_Symbol, px,Prices_Active, '
            f'qty, MAP(sym, LAMBDA(s, IF(s="",0, SUMIFS(Trades!$J$4:$J${3+N_TRADE_ROWS}, Trades!$D$4:$D${3+N_TRADE_ROWS}, s, Trades!$B$4:$B${3+N_TRADE_ROWS}, "<="&A{excel_r}+1)))) ,'
            f'SUMPRODUCT(qty, px))',
            f["calc"]
        )

        sh_equity.write_formula(r, 1, f"=F{excel_r}+G{excel_r}", f["calc"])
        sh_equity.write_formula(r, 2, f"=B{excel_r}" if i == 0 else f"=MAX(C{excel_r-1},B{excel_r})", f["calc"])
        sh_equity.write_formula(r, 3, f"=B{excel_r}-C{excel_r}", f["calc"])
        sh_equity.write_formula(r, 4, f"=IF(C{excel_r}=0,0,D{excel_r}/C{excel_r})", f["pct"])

    sh_equity.set_column(0,0,12,f["date"])
    sh_equity.set_column(1,3,14,f["money"])
    sh_equity.set_column(4,4,12,f["pct"])
    sh_equity.set_column(5,6,16,f["money"])
    sh_equity.freeze_panes(3, 0)

    chart_equity = wb.add_chart({"type":"line"})
    chart_equity.add_series({
        "name": "Equity",
        "categories": f"=Equity_Curve!$A$4:$A${3+N_DAYS}",
        "values":     f"=Equity_Curve!$B$4:$B${3+N_DAYS}",
        "line": {"width": 2.25}
    })
    chart_equity.set_title({"name":"Equity curve"})
    chart_equity.set_style(10)
    sh_equity.insert_chart("I4", chart_equity, {"x_scale": 1.4, "y_scale": 1.2})

    chart_dd = wb.add_chart({"type":"area"})
    chart_dd.add_series({
        "name": "Drawdown %",
        "categories": f"=Equity_Curve!$A$4:$A${3+N_DAYS}",
        "values":     f"=Equity_Curve!$E$4:$E${3+N_DAYS}",
        "fill": {"color":"#EF4444", "transparency": 25},
        "border": {"none": True}
    })
    chart_dd.set_title({"name":"Drawdown"})
    chart_dd.set_style(12)
    sh_equity.insert_chart("I22", chart_dd, {"x_scale": 1.4, "y_scale": 1.0})

    # ---------------- Drawdown summary ----------------
    sh_dd.write("A1", "Drawdown summary", f["title"])
    sh_dd.write("A3", "Worst drawdown %", f["cell"])
    sh_dd.write_formula("B3", f"=MIN(Equity_Curve!$E$4:$E${3+N_DAYS})", f["pct"])
    sh_dd.write("A4", "Current drawdown %", f["cell"])
    sh_dd.write_formula("B4", f"=LOOKUP(2,1/(Equity_Curve!$A$4:$A${3+N_DAYS}<>\"\"),Equity_Curve!$E$4:$E${3+N_DAYS})", f["pct"])
    sh_dd.write("A5", "Current equity", f["cell"])
    sh_dd.write_formula("B5", f"=LOOKUP(2,1/(Equity_Curve!$A$4:$A${3+N_DAYS}<>\"\"),Equity_Curve!$B$4:$B${3+N_DAYS})", f["money"])
    set_cols(sh_dd, [22, 16, 16])

    # ---------------- FIFO scaffolding ----------------
    sh_fifo.write("A1", "FIFO lots (manual match-ready; tax-grade auditability)", f["title"])
    sh_fifo.write("A3", "You can match SELLs to BUY lots in Realized_PnL_FIFO (supports partial sells).", f["note"])
    fifo_headers = ["LotID","BuyTradeID","BuyTimestamp","Symbol","QtyBought","QtyRemaining","BuyPrice","Fees","CostBasisRemaining"]
    for j,h in enumerate(fifo_headers):
        sh_fifo.write(5, j, h, f["h"])
    set_cols(sh_fifo, [10,12,18,10,12,14,10,10,18])

    sh_real.write("A1", "Realized P/L FIFO (match table)", f["title"])
    sh_real.write("A3", "For each SELL, allocate matched quantities to oldest BUY lots.", f["note"])
    r_headers = [
        "MatchID","SellTradeID","SellTimestamp","Symbol","SellQty","SellPrice","SellFees",
        "BuyLotID","BuyTradeID","BuyTimestamp","MatchedQty","BuyPrice","FeesAllocated",
        "Proceeds","CostBasis","RealizedPnL","HoldingDays"
    ]
    for j,h in enumerate(r_headers):
        sh_real.write(5, j, h, f["h"])
    sh_real.write("N4", "Total Realized P/L", f["cell"])
    sh_real.write_formula("O4", "=SUM($P$7:$P$5006)", f["money"])

    for r in range(6, 6 + N_TRADE_ROWS):
        excel_r = r + 1
        for c in range(0, 13):
            sh_real.write_blank(r, c, None, f["input"])
        sh_real.write_formula(r, 13, f"=K{excel_r}*F{excel_r}-M{excel_r}", f["calc"])
        sh_real.write_formula(r, 14, f"=K{excel_r}*L{excel_r}", f["calc"])
        sh_real.write_formula(r, 15, f"=N{excel_r}-O{excel_r}", f["calc"])
        sh_real.write_formula(r, 16, f"=IF(OR(C{excel_r}=\"\",J{excel_r}=\"\"),\"\",C{excel_r}-J{excel_r})", f["calc"])
    set_cols(sh_real, [10,12,18,10,10,10,10,10,12,18,12,10,12,12,12,12,12])

    # ---------------- Dashboard ----------------
    sh_dash.write("A1", "Pro Trader Dashboard", f["title"])
    sh_dash.write("A3", "KPIs", f["h"])
    sh_dash.write("A4", "Total value", f["kpi"]);        sh_dash.write_formula("B4", "=Drawdown!B5", f["money"])
    sh_dash.write("A5", "Max drawdown %", f["kpi"]);     sh_dash.write_formula("B5", "=Drawdown!B3", f["pct"])
    sh_dash.write("A6", "Current drawdown %", f["kpi"]); sh_dash.write_formula("B6", "=Drawdown!B4", f["pct"])
    sh_dash.write("A7", "Realized P/L (FIFO)", f["kpi"]);sh_dash.write_formula("B7", "=Realized_PnL_FIFO!O4", f["money"])
    sh_dash.write("D4", "Price source", f["cell"]);      sh_dash.write_formula("E4", "=PriceSource", f["calc"])
    set_cols(sh_dash, [18,18,4,18,18])

    sh_dash.insert_chart("A11", chart_equity, {"x_scale": 1.1, "y_scale": 1.0})
    sh_dash.insert_chart("A27", chart_dd, {"x_scale": 1.1, "y_scale": 0.9})

    # ---------------- Risk scenarios ----------------
    sh_risk.write("A1", "Scenario & risk tools", f["title"])
    sh_risk.write("A3", "Market shock", f["cell"]); sh_risk.write("B3", "-10%", f["input"])
    sh_risk.data_validation("B3", {"validate":"list", "source":["-10%","-20%","-50%","Custom"]})
    sh_risk.write("A4", "Custom shock %", f["cell"]); sh_risk.write_number("B4", -0.25, f["input"])
    sh_risk.write("A6", "Shock factor", f["cell"])
    sh_risk.write_formula("B6", '=IF(B3="Custom",1+B4,1+VALUE(SUBSTITUTE(B3,"%",""))/100)', f["calc"])

    sh_risk.write("A8", "Shocked equity (latest)", f["cell"])
    sh_risk.write_formula(
        "B8",
        f'=LOOKUP(2,1/(Equity_Curve!$A$4:$A${3+N_DAYS}<>""),Equity_Curve!$F$4:$F${3+N_DAYS}) + '
        f'LOOKUP(2,1/(Equity_Curve!$A$4:$A${3+N_DAYS}<>""),Equity_Curve!$G$4:$G${3+N_DAYS})*B6',
        f["money"]
    )
    sh_risk.write("A9", "Capital at risk (value drop)", f["cell"])
    sh_risk.write_formula("B9", "=Drawdown!B5 - B8", f["money"])
    set_cols(sh_risk, [22, 18, 16])

    # ---------------- Audit checks ----------------
    sh_audit.write("A1", "Audit & error checks", f["title"])
    sh_audit.write("A3", "Check", f["h"]); sh_audit.write("B3", "Status", f["h"]); sh_audit.write("C3", "Details", f["h"])

    # Missing prices for enabled
    sh_audit.write("A4", "Missing active prices for enabled symbols", f["cell"])
    sh_audit.write_formula("B4",
        '=IF(COUNTIF(Prices!$H$4:$H$1003,"TRUE")=0,"PASS",'
        'IF(SUMPRODUCT(--(Prices!$H$4:$H$1003="TRUE"),--(Prices!$F$4:$F$1003=""))>0,"FAIL","PASS"))',
        f["calc"]
    )
    sh_audit.write_formula("C4", '=IF(B4="PASS","", "Some enabled symbols have blank ActivePrice")', f["calc"])

    # Oversold (negative holdings)
    sh_audit.write("A5", "Negative holdings (oversold)", f["cell"])
    sh_audit.write_formula("B5",
        '=LET(sym,Prices_Symbol, qty, MAP(sym, LAMBDA(s, IF(s="",0, SUMIF(Trades!$D$4:$D$5003, s, Trades!$J$4:$J$5003)))), '
        'IF(MIN(qty)<0,"FAIL","PASS"))',
        f["calc"]
    )
    sh_audit.write_formula("C5", '=IF(B5="PASS","", "At least one symbol has negative net quantity")', f["calc"])

    set_cols(sh_audit, [34, 10, 60])

    # ---------------- Help ----------------
    sh_help.write("A1", "How to use", f["title"])
    sh_help.write("A3", "1) Enable symbols in Symbols.", f["note"])
    sh_help.write("A4", "2) Enter prices in Prices; switch source in Settings.", f["note"])
    sh_help.write("A5", "3) Enter trades in Trades (Timestamp must be real date/time).", f["note"])
    sh_help.write("A6", "4) Equity_Curve + Drawdown update automatically.", f["note"])
    sh_help.write("A7", "5) FIFO matching is audit-grade via Realized_PnL_FIFO match rows.", f["note"])

    wb.close()
    print(f"Created: {OUT_FILE}")

if __name__ == "__main__":
    build()
